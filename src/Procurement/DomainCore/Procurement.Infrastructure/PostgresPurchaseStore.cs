using System.Text.Json;
using Dapper;
using Lab.BoundedContextContracts.Procurement.IntegrationEvents;
using Npgsql;
using Procurement.Applications;
using Procurement.Domains;

namespace Procurement.Infrastructure;

/// <summary>Capability-specific PostgreSQL commits for one Procurement aggregate and its receipt source outbox.</summary>
public sealed class PostgresPurchaseStore(NpgsqlDataSource dataSource) :
    IPurchaseOrderQueries, IPurchaseCreationCommitter, IPurchaseSubmissionCommitter, IGoodsReceiptCommitter
{
    static PostgresPurchaseStore() => DefaultTypeMap.MatchNamesWithUnderscores = true;

    public async Task<CreatePurchaseResult> CreateOrGetAsync(PurchaseOrder candidate, CancellationToken cancellationToken)
    {
        await using var connection = await dataSource.OpenConnectionAsync(cancellationToken);
        const string insert = """
            INSERT INTO procurement_purchase_orders
            (id,client_request_id,product_id,supplier_sku,quantity,unit_price,currency,provider,
             state,supplier_order_id,received_quantity,version,created_at,updated_at)
            VALUES (@Id,@ClientRequestId,@ProductId,@SupplierSku,@Quantity,@UnitPrice,@Currency,@Provider,
                    @State,NULL,0,0,@CreatedAt,@CreatedAt)
            ON CONFLICT (client_request_id) DO NOTHING
            """;
        var count = await connection.ExecuteAsync(new CommandDefinition(insert, new
        {
            candidate.Id,
            candidate.Identity.ClientRequestId,
            candidate.Identity.ProductId,
            candidate.Identity.SupplierSku,
            candidate.Identity.Quantity,
            candidate.Identity.UnitPrice,
            candidate.Identity.Currency,
            candidate.Identity.Provider,
            State = candidate.State.ToString(),
            candidate.CreatedAt
        }, cancellationToken: cancellationToken));
        var order = await LoadByClientRequestAsync(connection, candidate.Identity.ClientRequestId, null, cancellationToken)
            ?? throw new InvalidOperationException("Committed purchase order could not be loaded.");
        return new CreatePurchaseResult(order, count == 1);
    }

    public async Task<PurchaseOrder?> FindByIdAsync(Guid id, CancellationToken cancellationToken)
    {
        await using var connection = await dataSource.OpenConnectionAsync(cancellationToken);
        return await LoadByIdAsync(connection, id, null, false, cancellationToken);
    }

    public async Task<IReadOnlyList<PurchaseOrder>> RecentAsync(int limit, CancellationToken cancellationToken)
    {
        await using var connection = await dataSource.OpenConnectionAsync(cancellationToken);
        var ids = await connection.QueryAsync<Guid>(new CommandDefinition(
            "SELECT id FROM procurement_purchase_orders ORDER BY created_at DESC, id DESC LIMIT @Limit",
            new { Limit = Math.Clamp(limit, 1, 100) }, cancellationToken: cancellationToken));
        var result = new List<PurchaseOrder>();
        foreach (var id in ids)
        {
            var order = await LoadByIdAsync(connection, id, null, false, cancellationToken);
            if (order is not null) result.Add(order);
        }
        return result;
    }

    public Task<PurchaseOrder> ApplyOutcomeAsync(Guid id, SupplierOrderOutcome outcome,
        CancellationToken cancellationToken) => ChangeSubmissionAsync(id,
        order => order.ApplySupplierOutcome(outcome.Accepted, outcome.SupplierOrderId, DateTimeOffset.UtcNow), cancellationToken);

    public Task<PurchaseOrder> MarkUnknownAsync(Guid id, CancellationToken cancellationToken) =>
        ChangeSubmissionAsync(id, order => order.MarkUnknown(DateTimeOffset.UtcNow), cancellationToken);

    private async Task<PurchaseOrder> ChangeSubmissionAsync(Guid id, Action<PurchaseOrder> decide,
        CancellationToken cancellationToken)
    {
        await using var connection = await dataSource.OpenConnectionAsync(cancellationToken);
        await using var transaction = await connection.BeginTransactionAsync(cancellationToken);
        var order = await LoadByIdAsync(connection, id, transaction, true, cancellationToken)
            ?? throw new ProcurementRuleException("purchase_not_found", "Purchase order was not found.");
        var oldVersion = order.Version;
        decide(order);
        if (order.Version != oldVersion)
        {
            await connection.ExecuteAsync(new CommandDefinition("""
                UPDATE procurement_purchase_orders SET state=@State,supplier_order_id=@SupplierOrderId,
                    version=@Version,updated_at=@UpdatedAt WHERE id=@Id
                """, new { order.Id, State = order.State.ToString(), order.SupplierOrderId, order.Version, order.UpdatedAt },
                transaction, cancellationToken: cancellationToken));
        }
        await transaction.CommitAsync(cancellationToken);
        return order;
    }

    public async Task<ReceiveGoodsResult> CommitAsync(Guid purchaseOrderId, Guid receiptId,
        Func<PurchaseOrder, ReceiveGoodsResult> decide, CancellationToken cancellationToken)
    {
        await using var connection = await dataSource.OpenConnectionAsync(cancellationToken);
        await using var transaction = await connection.BeginTransactionAsync(cancellationToken);
        var order = await LoadByIdAsync(connection, purchaseOrderId, transaction, true, cancellationToken)
            ?? throw new ProcurementRuleException("purchase_not_found", "Purchase order was not found.");

        // The receipt key is global. A replay on a different order must not be mistaken for a fresh receipt.
        var priorOwner = await connection.QuerySingleOrDefaultAsync<Guid?>(new CommandDefinition(
            "SELECT purchase_order_id FROM procurement_receipts WHERE receipt_id=@ReceiptId",
            new { ReceiptId = receiptId }, transaction, cancellationToken: cancellationToken));
        if (priorOwner is not null && priorOwner != purchaseOrderId)
            throw new ProcurementRuleException("receipt_identity_conflict", "ReceiptId already belongs to a different order.");

        var result = decide(order);
        if (!result.Created)
        {
            await transaction.CommitAsync(cancellationToken);
            return result;
        }

        try
        {
            await connection.ExecuteAsync(new CommandDefinition("""
                UPDATE procurement_purchase_orders SET state=@State,received_quantity=@ReceivedQuantity,
                    version=@Version,updated_at=@UpdatedAt WHERE id=@Id
                """, new { order.Id, State = order.State.ToString(), order.ReceivedQuantity, order.Version, order.UpdatedAt },
                transaction, cancellationToken: cancellationToken));
            await connection.ExecuteAsync(new CommandDefinition("""
                INSERT INTO procurement_receipts(receipt_id,purchase_order_id,product_id,quantity,received_at)
                VALUES (@ReceiptId,@PurchaseOrderId,@ProductId,@Quantity,@ReceivedAt)
                """, result.Receipt, transaction, cancellationToken: cancellationToken));
            var message = new GoodsReceived(result.Receipt.ReceiptId, result.Receipt.PurchaseOrderId,
                result.Receipt.ProductId, result.Receipt.Quantity, result.Receipt.ReceivedAt);
            await connection.ExecuteAsync(new CommandDefinition("""
                INSERT INTO procurement_outbox(id,partition_key,payload)
                VALUES (@Id,@PartitionKey,CAST(@Payload AS jsonb))
                """, new { Id = receiptId, PartitionKey = order.Identity.ProductId.ToString("N"),
                    Payload = JsonSerializer.Serialize(message) }, transaction, cancellationToken: cancellationToken));
            await transaction.CommitAsync(cancellationToken);
            return result;
        }
        catch (PostgresException ex) when (ex.SqlState == PostgresErrorCodes.UniqueViolation)
        {
            throw new ProcurementRuleException("receipt_identity_conflict", "ReceiptId already has different contents.");
        }
    }

    private static async Task<PurchaseOrder?> LoadByClientRequestAsync(NpgsqlConnection connection, Guid clientRequestId,
        NpgsqlTransaction? transaction, CancellationToken cancellationToken)
    {
        var row = await connection.QuerySingleOrDefaultAsync<PurchaseRow>(new CommandDefinition(
            "SELECT * FROM procurement_purchase_orders WHERE client_request_id=@ClientRequestId",
            new { ClientRequestId = clientRequestId }, transaction, cancellationToken: cancellationToken));
        return row is null ? null : await RestoreAsync(connection, row, transaction, cancellationToken);
    }

    private static async Task<PurchaseOrder?> LoadByIdAsync(NpgsqlConnection connection, Guid id,
        NpgsqlTransaction? transaction, bool forUpdate, CancellationToken cancellationToken)
    {
        var row = await connection.QuerySingleOrDefaultAsync<PurchaseRow>(new CommandDefinition(
            "SELECT * FROM procurement_purchase_orders WHERE id=@Id" + (forUpdate ? " FOR UPDATE" : ""),
            new { Id = id }, transaction, cancellationToken: cancellationToken));
        return row is null ? null : await RestoreAsync(connection, row, transaction, cancellationToken);
    }

    private static async Task<PurchaseOrder> RestoreAsync(NpgsqlConnection connection, PurchaseRow row,
        NpgsqlTransaction? transaction, CancellationToken cancellationToken)
    {
        var receipts = await connection.QueryAsync<GoodsReceipt>(new CommandDefinition(
            "SELECT receipt_id AS ReceiptId,purchase_order_id AS PurchaseOrderId,product_id AS ProductId,quantity,received_at AS ReceivedAt FROM procurement_receipts WHERE purchase_order_id=@Id ORDER BY received_at,receipt_id",
            new { row.Id }, transaction, cancellationToken: cancellationToken));
        return PurchaseOrder.Restore(row.Id,
            new PurchaseIdentity(row.ClientRequestId, row.ProductId, row.SupplierSku, row.Quantity,
                row.UnitPrice, row.Currency, row.Provider),
            Enum.Parse<PurchaseOrderState>(row.State, false), row.SupplierOrderId,
            row.ReceivedQuantity, row.Version, row.CreatedAt, row.UpdatedAt, receipts);
    }

    private sealed class PurchaseRow
    {
        public Guid Id { get; set; }
        public Guid ClientRequestId { get; set; }
        public Guid ProductId { get; set; }
        public string SupplierSku { get; set; } = "";
        public int Quantity { get; set; }
        public decimal UnitPrice { get; set; }
        public string Currency { get; set; } = "";
        public string Provider { get; set; } = "";
        public string State { get; set; } = "";
        public string? SupplierOrderId { get; set; }
        public int ReceivedQuantity { get; set; }
        public int Version { get; set; }
        public DateTimeOffset CreatedAt { get; set; }
        public DateTimeOffset UpdatedAt { get; set; }
    }
}
