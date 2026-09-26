using System.Text.Json;
using Dapper;
using Npgsql;
using Procurement.Applications;
using Procurement.Domains;
using Procurement.Infrastructure;

namespace Procurement.Tests;

public sealed class ReceiptPostgresScenarios
{
    // R03/R04/R06/R08-source / AC02: real PG receipt+outbox atomicity, replay and competing overreceipt.
    // Broker delivery and Inventory stock effects remain separate external scenarios.
    [ExternalIntegrationFact, Trait("Scenario", "R03-R04-R06-R08-source")]
    public async Task Receipt_transaction_is_durable_and_race_safe()
    {
        await using var dataSource = NpgsqlDataSource.Create(
            Environment.GetEnvironmentVariable(ExternalIntegrationFactAttribute.ConnectionVariable)!);
        await GivenAdditiveSchema(dataSource);
        var identity = new PurchaseIdentity(Guid.NewGuid(), Guid.NewGuid(), "REAL-001", 10, 100m, "TWD", "direct");
        var store = new PostgresPurchaseStore(dataSource);
        var order = await GivenAcceptedPurchase(store, identity);
        try
        {
            var firstId = Guid.NewGuid();
            var first = await WhenReceiving(store, order.Id, firstId, 6);
            var replay = await WhenReceiving(store, order.Id, firstId, 6);
            await ThenReplayHasOneDurableOutbox(dataSource, first, replay, firstId, identity.ProductId);

            var changed = await WhenReceivingInvalid(store, order.Id, firstId, 5);
            ThenChangedReceiptConflicts(changed);

            var competing = await WhenTwoSixUnitReceiptsCompete(store, order.Id);
            await ThenConcurrentOverreceiptIsRejected(dataSource, order.Id, competing);
        }
        finally { await CleanupOwnRows(dataSource, order.Id); }
    }

    private static async Task GivenAdditiveSchema(NpgsqlDataSource dataSource)
    {
        var sql = await File.ReadAllTextAsync(Path.Combine(AppContext.BaseDirectory, "Schema", "procurement.sql"));
        await using var connection = await dataSource.OpenConnectionAsync();
        await using var command = new NpgsqlCommand(sql, connection);
        await command.ExecuteNonQueryAsync();
    }

    private static async Task<PurchaseOrder> GivenAcceptedPurchase(PostgresPurchaseStore store, PurchaseIdentity identity)
    {
        var created = await store.CreateOrGetAsync(PurchaseOrder.Create(Guid.NewGuid(), identity, DateTimeOffset.UtcNow),
            CancellationToken.None);
        Assert.True(created.Created);
        return await store.ApplyOutcomeAsync(created.Order.Id, new SupplierOrderOutcome(true, "vendor-pg"), CancellationToken.None);
    }

    private static Task<ReceiveGoodsResult> WhenReceiving(PostgresPurchaseStore store, Guid orderId, Guid receiptId, int quantity) =>
        new ReceiveGoodsUseCase(store).ExecuteAsync(new ReceiveGoods(orderId, receiptId, quantity), CancellationToken.None);
    private static ValueTask<Exception?> WhenReceivingInvalid(PostgresPurchaseStore store, Guid orderId, Guid receiptId, int quantity) =>
        Record.ExceptionAsync(() => WhenReceiving(store, orderId, receiptId, quantity));
    private static async Task<Exception?[]> WhenTwoSixUnitReceiptsCompete(PostgresPurchaseStore store, Guid orderId)
    {
        var left = Guid.NewGuid();
        var right = Guid.NewGuid();
        return await Task.WhenAll(
            Record.ExceptionAsync(() => WhenReceiving(store, orderId, left, 6)).AsTask(),
            Record.ExceptionAsync(() => WhenReceiving(store, orderId, right, 6)).AsTask());
    }

    private static async Task ThenReplayHasOneDurableOutbox(NpgsqlDataSource dataSource,
        ReceiveGoodsResult first, ReceiveGoodsResult replay, Guid receiptId, Guid productId)
    {
        Assert.True(first.Created);
        Assert.False(replay.Created);
        Assert.Equal(first.Receipt, replay.Receipt);
        await using var connection = await dataSource.OpenConnectionAsync();
        var rows = await connection.QueryAsync<(Guid Id, string PartitionKey, string Payload)>(
            "SELECT id,partition_key,payload::text AS payload FROM procurement_outbox WHERE id=@Id",
            new { Id = receiptId });
        var row = Assert.Single(rows);
        Assert.Equal(productId.ToString("N"), row.PartitionKey);
        using var document = JsonDocument.Parse(row.Payload);
        Assert.Equal(receiptId, document.RootElement.GetProperty("receiptId").GetGuid());
        Assert.Equal(6, document.RootElement.GetProperty("quantity").GetInt32());
    }

    private static void ThenChangedReceiptConflicts(Exception? error) =>
        Assert.Equal("receipt_identity_conflict", Assert.IsType<ProcurementRuleException>(error).Code);

    private static async Task ThenConcurrentOverreceiptIsRejected(NpgsqlDataSource dataSource, Guid orderId,
        IReadOnlyList<Exception?> competing)
    {
        Assert.All(competing, error => Assert.Equal("over_receipt", Assert.IsType<ProcurementRuleException>(error).Code));
        await using var connection = await dataSource.OpenConnectionAsync();
        var order = await connection.QuerySingleAsync<(int ReceivedQuantity, string State)>(
            "SELECT received_quantity,state FROM procurement_purchase_orders WHERE id=@Id", new { Id = orderId });
        Assert.Equal(6, order.ReceivedQuantity);
        Assert.Equal("PartiallyReceived", order.State);
        Assert.Equal(1, await connection.ExecuteScalarAsync<int>(
            "SELECT count(*) FROM procurement_receipts WHERE purchase_order_id=@Id", new { Id = orderId }));
    }

    private static async Task CleanupOwnRows(NpgsqlDataSource dataSource, Guid orderId)
    {
        await using var connection = await dataSource.OpenConnectionAsync();
        await connection.ExecuteAsync("DELETE FROM procurement_outbox WHERE id IN (SELECT receipt_id FROM procurement_receipts WHERE purchase_order_id=@Id)", new { Id = orderId });
        await connection.ExecuteAsync("DELETE FROM procurement_receipts WHERE purchase_order_id=@Id", new { Id = orderId });
        await connection.ExecuteAsync("DELETE FROM procurement_purchase_orders WHERE id=@Id", new { Id = orderId });
    }
}
