using System.Text.Json;
using Dapper;
using Npgsql;
using Procurement.Applications;
using Procurement.Domains;
using Procurement.Infrastructure;

namespace Procurement.Tests;

public sealed class ReceiptPostgresScenarios
{
    // R02 / AC02: invalid follow-up quantities cannot change the stored partial receipt or source outbox.
    [ExternalIntegrationFact, Trait("Scenario", "R02")]
    public async Task Invalid_follow_up_receipts_leave_postgres_facts_unchanged()
    {
        await using var dataSource = NpgsqlDataSource.Create(
            Environment.GetEnvironmentVariable(ExternalIntegrationFactAttribute.ConnectionVariable)!);
        await GivenAdditiveSchema(dataSource);
        var store = new PostgresPurchaseStore(dataSource);
        var identity = new PurchaseIdentity(Guid.NewGuid(), Guid.NewGuid(), "REAL-001", 10, 100m, "TWD", "direct");
        var orderId = Guid.NewGuid();
        try
        {
            await GivenAcceptedPurchase(store, identity, orderId);
            await WhenReceiving(store, orderId, Guid.NewGuid(), 6);
            foreach (var quantity in new[] { 5, 0, -1 })
            {
                var attemptedReceiptId = Guid.NewGuid();
                var error = await WhenReceivingInvalid(store, orderId, attemptedReceiptId, quantity);
                ThenInvalidReceiptIsRejected(error, quantity);
                await ThenPartialReceiptFactsRemain(dataSource, orderId);
                await ThenNoFactWasCreatedForAttempt(dataSource, attemptedReceiptId);
            }
        }
        finally { await CleanupOwnRows(dataSource, orderId); }
    }

    // R03 / AC02: a replay after source-outbox retention still returns the original receipt without restaging it.
    [ExternalIntegrationFact, Trait("Scenario", "R03-after-outbox-purge")]
    public async Task Replay_after_source_outbox_deletion_does_not_recreate_event()
    {
        await using var dataSource = NpgsqlDataSource.Create(
            Environment.GetEnvironmentVariable(ExternalIntegrationFactAttribute.ConnectionVariable)!);
        await GivenAdditiveSchema(dataSource);
        var store = new PostgresPurchaseStore(dataSource);
        var identity = new PurchaseIdentity(Guid.NewGuid(), Guid.NewGuid(), "REAL-001", 10, 100m, "TWD", "direct");
        var orderId = Guid.NewGuid();
        try
        {
            await GivenAcceptedPurchase(store, identity, orderId);
            var receiptId = Guid.NewGuid();
            var first = await WhenReceiving(store, orderId, receiptId, 10);
            await WhenDeletingOwnSourceOutbox(dataSource, receiptId);
            var replay = await WhenReceiving(store, orderId, receiptId, 10);
            await ThenReplayAfterPurgeHasNoSecondEffect(dataSource, orderId, receiptId, first, replay);
        }
        finally { await CleanupOwnRows(dataSource, orderId); }
    }

    // R04 / AC02: a receipt ID is global across orders, including orders for different products.
    [ExternalIntegrationFact, Trait("Scenario", "R04-cross-purchase-product")]
    public async Task Receipt_id_cannot_move_to_another_purchase_or_product()
    {
        await using var dataSource = NpgsqlDataSource.Create(
            Environment.GetEnvironmentVariable(ExternalIntegrationFactAttribute.ConnectionVariable)!);
        await GivenAdditiveSchema(dataSource);
        var store = new PostgresPurchaseStore(dataSource);
        var firstIdentity = new PurchaseIdentity(Guid.NewGuid(), Guid.NewGuid(), "REAL-001", 10, 100m, "TWD", "direct");
        var secondIdentity = firstIdentity with { ClientRequestId = Guid.NewGuid(), ProductId = Guid.NewGuid() };
        var firstOrderId = Guid.NewGuid();
        var secondOrderId = Guid.NewGuid();
        try
        {
            await GivenAcceptedPurchase(store, firstIdentity, firstOrderId);
            await GivenAcceptedPurchase(store, secondIdentity, secondOrderId);
            var receiptId = Guid.NewGuid();
            await WhenReceiving(store, firstOrderId, receiptId, 4);
            var error = await WhenReceivingInvalid(store, secondOrderId, receiptId, 4);
            await ThenCrossPurchaseReplayConflictsWithoutMutation(dataSource, firstOrderId, secondOrderId, receiptId, error);
        }
        finally
        {
            await CleanupOwnRows(dataSource, firstOrderId);
            await CleanupOwnRows(dataSource, secondOrderId);
        }
    }

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
        var orderId = Guid.NewGuid();
        try
        {
            var order = await GivenAcceptedPurchase(store, identity, orderId);
            var firstId = Guid.NewGuid();
            var first = await WhenReceiving(store, order.Id, firstId, 6);
            var replay = await WhenReceiving(store, order.Id, firstId, 6);
            await ThenReplayHasOneDurableOutbox(dataSource, first, replay, firstId, identity.ProductId);

            var changed = await WhenReceivingInvalid(store, order.Id, firstId, 5);
            ThenChangedReceiptConflicts(changed);

            var competing = await WhenTwoFourUnitReceiptsCompete(store, order.Id);
            await ThenConcurrentOverreceiptIsRejected(dataSource, order.Id, competing);
        }
        finally { await CleanupOwnRows(dataSource, orderId); }
    }

    // R05 / AC02: concurrent same-key receipt requests converge on one stored fact and event.
    [ExternalIntegrationFact, Trait("Scenario", "R05")]
    public async Task Concurrent_matching_receipt_has_one_commit()
    {
        await using var dataSource = NpgsqlDataSource.Create(
            Environment.GetEnvironmentVariable(ExternalIntegrationFactAttribute.ConnectionVariable)!);
        await GivenAdditiveSchema(dataSource);
        var store = new PostgresPurchaseStore(dataSource);
        var identity = new PurchaseIdentity(Guid.NewGuid(), Guid.NewGuid(), "REAL-001", 10, 100m, "TWD", "direct");
        var orderId = Guid.NewGuid();
        try
        {
            var order = await GivenAcceptedPurchase(store, identity, orderId);
            var receiptId = Guid.NewGuid();
            var outcomes = await WhenSameReceiptIsConcurrent(store, order.Id, receiptId);
            await ThenConcurrentReplayHasOneCommit(dataSource, order.Id, receiptId, outcomes);
        }
        finally { await CleanupOwnRows(dataSource, orderId); }
    }

    // R06 read projection / AC02: multi-statement reads stay internally coherent during partial receipts.
    [ExternalIntegrationFact, Trait("Scenario", "R06-read-snapshot")]
    public async Task Concurrent_receipts_never_expose_mixed_read_snapshot()
    {
        await using var dataSource = NpgsqlDataSource.Create(
            Environment.GetEnvironmentVariable(ExternalIntegrationFactAttribute.ConnectionVariable)!);
        await GivenAdditiveSchema(dataSource);
        var store = new PostgresPurchaseStore(dataSource);
        var identity = new PurchaseIdentity(Guid.NewGuid(), Guid.NewGuid(), "REAL-001", 10, 100m, "TWD", "direct");
        var orderId = Guid.NewGuid();
        try
        {
            await GivenAcceptedPurchase(store, identity, orderId);
            var snapshots = await WhenReadingWhileTwoReceiptsCommit(store, orderId);
            ThenEverySnapshotMatchesItsReceiptFacts(snapshots);
            var final = await store.GetByIdAsync(orderId, CancellationToken.None);
            Assert.NotNull(final);
            Assert.Equal(10, final.ReceivedQuantity);
            Assert.Equal(2, final.Receipts.Count);
        }
        finally { await CleanupOwnRows(dataSource, orderId); }
    }

    private static async Task GivenAdditiveSchema(NpgsqlDataSource dataSource)
    {
        var sql = await File.ReadAllTextAsync(Path.Combine(AppContext.BaseDirectory, "Schema", "procurement.sql"));
        await using var connection = await dataSource.OpenConnectionAsync();
        await using var command = new NpgsqlCommand(sql, connection);
        await command.ExecuteNonQueryAsync();
    }

    private static async Task<PurchaseOrder> GivenAcceptedPurchase(PostgresPurchaseStore store,
        PurchaseIdentity identity, Guid orderId)
    {
        var created = await store.CreateOrGetAsync(PurchaseOrder.Create(orderId, identity, DateTimeOffset.UtcNow),
            CancellationToken.None);
        Assert.True(created.Created);
        return await store.ApplyOutcomeAsync(created.Order.Id, new SupplierOrderOutcome(true, "vendor-pg"), CancellationToken.None);
    }

    private static Task<ReceiveGoodsOutput> WhenReceiving(PostgresPurchaseStore store, Guid orderId, Guid receiptId, int quantity) =>
        new ReceiveGoodsUseCase(store).ExecuteAsync(new ReceiveGoodsInput(orderId, receiptId, quantity), CancellationToken.None);
    private static ValueTask<Exception?> WhenReceivingInvalid(PostgresPurchaseStore store, Guid orderId, Guid receiptId, int quantity) =>
        Record.ExceptionAsync(() => WhenReceiving(store, orderId, receiptId, quantity));
    private static async Task<Exception?[]> WhenTwoFourUnitReceiptsCompete(PostgresPurchaseStore store, Guid orderId)
    {
        var left = Guid.NewGuid();
        var right = Guid.NewGuid();
        return await Task.WhenAll(
            Record.ExceptionAsync(() => WhenReceiving(store, orderId, left, 4)).AsTask(),
            Record.ExceptionAsync(() => WhenReceiving(store, orderId, right, 4)).AsTask());
    }

    private static Task<ReceiveGoodsOutput[]> WhenSameReceiptIsConcurrent(PostgresPurchaseStore store,
        Guid orderId, Guid receiptId) => Task.WhenAll(
        WhenReceiving(store, orderId, receiptId, 4),
        WhenReceiving(store, orderId, receiptId, 4));

    private static async Task<IReadOnlyList<PurchaseOrderResponse>> WhenReadingWhileTwoReceiptsCommit(
        PostgresPurchaseStore store, Guid orderId)
    {
        var begin = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
        var reader = Task.Run(async () =>
        {
            var observed = new List<PurchaseOrderResponse>();
            begin.SetResult(true);
            for (var attempt = 0; attempt < 40; attempt++)
            {
                var current = await store.GetByIdAsync(orderId, CancellationToken.None);
                Assert.NotNull(current);
                observed.Add(current);
                if (attempt % 5 == 0)
                {
                    var recent = await store.RecentAsync(100, CancellationToken.None);
                    var listed = recent.FirstOrDefault(x => x.Id == orderId);
                    if (listed is not null) observed.Add(listed);
                }
                await Task.Delay(1);
            }
            return observed;
        });
        var writer = Task.Run(async () =>
        {
            await begin.Task;
            await Task.Delay(5);
            await WhenReceiving(store, orderId, Guid.NewGuid(), 6);
            await Task.Delay(5);
            await WhenReceiving(store, orderId, Guid.NewGuid(), 4);
        });
        await Task.WhenAll(reader, writer);
        return await reader;
    }

    private static void ThenEverySnapshotMatchesItsReceiptFacts(IReadOnlyList<PurchaseOrderResponse> snapshots)
    {
        Assert.NotEmpty(snapshots);
        Assert.All(snapshots, snapshot =>
        {
            Assert.Equal(snapshot.ReceivedQuantity, snapshot.Receipts.Sum(receipt => receipt.Quantity));
            Assert.InRange(snapshot.ReceivedQuantity, 0, snapshot.Identity.Quantity);
        });
    }

    private static async Task ThenReplayHasOneDurableOutbox(NpgsqlDataSource dataSource,
        ReceiveGoodsOutput first, ReceiveGoodsOutput replay, Guid receiptId, Guid productId)
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
        Assert.Equal(first.Receipt.ReceivedAt,
            document.RootElement.GetProperty("receivedAt").GetDateTimeOffset());
        Assert.Equal(0, first.Receipt.ReceivedAt.Ticks % TimeSpan.TicksPerMillisecond);
    }

    private static void ThenChangedReceiptConflicts(Exception? error) =>
        Assert.Equal("receipt_identity_conflict", Assert.IsType<ProcurementRuleException>(error).Code);

    private static void ThenInvalidReceiptIsRejected(Exception? error, int quantity) =>
        Assert.Equal(quantity > 0 ? "over_receipt" : "invalid_receipt",
            Assert.IsType<ProcurementRuleException>(error).Code);

    private static async Task ThenPartialReceiptFactsRemain(NpgsqlDataSource dataSource, Guid orderId)
    {
        await using var connection = await dataSource.OpenConnectionAsync();
        var state = await connection.QuerySingleAsync<(int ReceivedQuantity, string State)>(
            "SELECT received_quantity,state FROM procurement_purchase_orders WHERE id=@Id", new { Id = orderId });
        Assert.Equal(6, state.ReceivedQuantity);
        Assert.Equal("PartiallyReceived", state.State);
        Assert.Equal(1, await connection.ExecuteScalarAsync<int>(
            "SELECT count(*) FROM procurement_receipts WHERE purchase_order_id=@Id", new { Id = orderId }));
        Assert.Equal(1, await connection.ExecuteScalarAsync<int>(
            "SELECT count(*) FROM procurement_outbox WHERE id IN (SELECT receipt_id FROM procurement_receipts WHERE purchase_order_id=@Id)",
            new { Id = orderId }));
    }

    private static async Task ThenNoFactWasCreatedForAttempt(NpgsqlDataSource dataSource, Guid receiptId)
    {
        await using var connection = await dataSource.OpenConnectionAsync();
        Assert.Equal(0, await connection.ExecuteScalarAsync<int>(
            "SELECT count(*) FROM procurement_receipts WHERE receipt_id=@Id", new { Id = receiptId }));
        Assert.Equal(0, await connection.ExecuteScalarAsync<int>(
            "SELECT count(*) FROM procurement_outbox WHERE id=@Id", new { Id = receiptId }));
    }

    private static async Task WhenDeletingOwnSourceOutbox(NpgsqlDataSource dataSource, Guid receiptId)
    {
        await using var connection = await dataSource.OpenConnectionAsync();
        Assert.Equal(1, await connection.ExecuteAsync("DELETE FROM procurement_outbox WHERE id=@Id", new { Id = receiptId }));
    }

    private static async Task ThenReplayAfterPurgeHasNoSecondEffect(NpgsqlDataSource dataSource, Guid orderId,
        Guid receiptId, ReceiveGoodsOutput first, ReceiveGoodsOutput replay)
    {
        Assert.True(first.Created);
        Assert.False(replay.Created);
        Assert.Equal(first.Receipt, replay.Receipt);
        Assert.Equal(first.Order.Version, replay.Order.Version);
        Assert.Equal(10, replay.Order.ReceivedQuantity);
        await using var connection = await dataSource.OpenConnectionAsync();
        Assert.Equal(1, await connection.ExecuteScalarAsync<int>(
            "SELECT count(*) FROM procurement_receipts WHERE receipt_id=@Id", new { Id = receiptId }));
        Assert.Equal(0, await connection.ExecuteScalarAsync<int>(
            "SELECT count(*) FROM procurement_outbox WHERE id=@Id", new { Id = receiptId }));
        Assert.Equal(10, await connection.ExecuteScalarAsync<int>(
            "SELECT received_quantity FROM procurement_purchase_orders WHERE id=@Id", new { Id = orderId }));
    }

    private static async Task ThenCrossPurchaseReplayConflictsWithoutMutation(NpgsqlDataSource dataSource,
        Guid firstOrderId, Guid secondOrderId, Guid receiptId, Exception? error)
    {
        ThenChangedReceiptConflicts(error);
        await using var connection = await dataSource.OpenConnectionAsync();
        Assert.Equal(4, await connection.ExecuteScalarAsync<int>(
            "SELECT received_quantity FROM procurement_purchase_orders WHERE id=@Id", new { Id = firstOrderId }));
        Assert.Equal(0, await connection.ExecuteScalarAsync<int>(
            "SELECT received_quantity FROM procurement_purchase_orders WHERE id=@Id", new { Id = secondOrderId }));
        Assert.Equal(1, await connection.ExecuteScalarAsync<int>(
            "SELECT count(*) FROM procurement_receipts WHERE receipt_id=@Id AND purchase_order_id=@OrderId",
            new { Id = receiptId, OrderId = firstOrderId }));
        Assert.Equal(0, await connection.ExecuteScalarAsync<int>(
            "SELECT count(*) FROM procurement_receipts WHERE purchase_order_id=@Id", new { Id = secondOrderId }));
        Assert.Equal(1, await connection.ExecuteScalarAsync<int>(
            "SELECT count(*) FROM procurement_outbox WHERE id=@Id", new { Id = receiptId }));
    }

    private static async Task ThenConcurrentOverreceiptIsRejected(NpgsqlDataSource dataSource, Guid orderId,
        IReadOnlyList<Exception?> competing)
    {
        Assert.Single(competing, error => error is null);
        Assert.Single(competing, error => error is ProcurementRuleException rule &&
            (rule.Code is "over_receipt" or "receipt_state_conflict"));
        await using var connection = await dataSource.OpenConnectionAsync();
        var order = await connection.QuerySingleAsync<(int ReceivedQuantity, string State)>(
            "SELECT received_quantity,state FROM procurement_purchase_orders WHERE id=@Id", new { Id = orderId });
        Assert.Equal(10, order.ReceivedQuantity);
        Assert.Equal("Received", order.State);
        Assert.Equal(2, await connection.ExecuteScalarAsync<int>(
            "SELECT count(*) FROM procurement_receipts WHERE purchase_order_id=@Id", new { Id = orderId }));
        Assert.Equal(2, await connection.ExecuteScalarAsync<int>(
            "SELECT count(*) FROM procurement_outbox WHERE id IN (SELECT receipt_id FROM procurement_receipts WHERE purchase_order_id=@Id)",
            new { Id = orderId }));
    }

    private static async Task ThenConcurrentReplayHasOneCommit(NpgsqlDataSource dataSource,
        Guid orderId, Guid receiptId, IReadOnlyList<ReceiveGoodsOutput> outcomes)
    {
        Assert.Equal(2, outcomes.Count);
        Assert.Single(outcomes, result => result.Created);
        Assert.Single(outcomes, result => !result.Created);
        Assert.Equal(outcomes[0].Receipt, outcomes[1].Receipt);
        Assert.Equal(0, outcomes[0].Receipt.ReceivedAt.Ticks % TimeSpan.TicksPerMillisecond);
        await using var connection = await dataSource.OpenConnectionAsync();
        Assert.Equal(4, await connection.ExecuteScalarAsync<int>(
            "SELECT received_quantity FROM procurement_purchase_orders WHERE id=@Id", new { Id = orderId }));
        Assert.Equal(1, await connection.ExecuteScalarAsync<int>(
            "SELECT count(*) FROM procurement_receipts WHERE receipt_id=@Id", new { Id = receiptId }));
        Assert.Equal(1, await connection.ExecuteScalarAsync<int>(
            "SELECT count(*) FROM procurement_outbox WHERE id=@Id", new { Id = receiptId }));
    }

    private static async Task CleanupOwnRows(NpgsqlDataSource dataSource, Guid orderId)
    {
        await using var connection = await dataSource.OpenConnectionAsync();
        await connection.ExecuteAsync("DELETE FROM procurement_outbox WHERE id IN (SELECT receipt_id FROM procurement_receipts WHERE purchase_order_id=@Id)", new { Id = orderId });
        await connection.ExecuteAsync("DELETE FROM procurement_receipts WHERE purchase_order_id=@Id", new { Id = orderId });
        await connection.ExecuteAsync("DELETE FROM procurement_purchase_orders WHERE id=@Id", new { Id = orderId });
    }
}
