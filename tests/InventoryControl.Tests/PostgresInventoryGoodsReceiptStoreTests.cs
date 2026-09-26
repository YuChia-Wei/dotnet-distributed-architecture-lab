using InventoryControl.Applications.Outbox;
using InventoryControl.Applications.Receipts;
using InventoryControl.Domains;
using InventoryControl.Infrastructure.Applications.Repositories;
using InventoryControl.Infrastructure.Persistence;
using Lab.BoundedContextContracts.Inventory.IntegrationEvents;
using Lab.BuildingBlocks.Application;
using Lab.BuildingBlocks.Integrations;
using Microsoft.EntityFrameworkCore;
using NSubstitute;
using Shouldly;

namespace InventoryControl.Tests;

/// <summary>R03–R07: receipt identity, one stock effect, rollback and retry against actual PostgreSQL.</summary>
public sealed class PostgresInventoryGoodsReceiptStoreTests
{
    [ExternalIntegrationFact]
    public async Task R03_given_a_completed_receipt_and_removed_outbox_when_replayed_then_original_outcome_is_returned_without_new_effects()
    {
        await using var database = await InventoryPostgresDatabase.CreateAsync();
        var item = await GivenStock(database, 5);
        var input = GivenReceipt(item.ProductId, 2);

        var first = await WhenApplying(database, input);
        await GivenOutboxWasRetainedThenRemoved(database, input.ReceiptId);
        await using var replayContext = database.CreateContext();
        var replay = await new PostgresInventoryGoodsReceiptStore(
            replayContext, Substitute.For<IDomainEventDispatcher>()).ApplyAndStageAsync(
                input,
                _ => throw new InvalidOperationException("Replay must not create an event."),
                CancellationToken.None);

        ThenOutcome(first, item.Id, 7, false);
        ThenOutcome(replay, item.Id, 7, true);
        await ThenDurableState(database, item.Id, 7, 1, 0);
    }

    [ExternalIntegrationFact]
    public async Task R04_given_a_completed_receipt_when_any_immutable_payload_field_changes_then_identity_conflicts_without_mutation()
    {
        await using var database = await InventoryPostgresDatabase.CreateAsync();
        var item = await GivenStock(database, 5);
        var input = GivenReceipt(item.ProductId, 2);
        await WhenApplying(database, input);
        var changed = new[]
        {
            input with { PurchaseOrderId = Guid.CreateVersion7() },
            input with { ProductId = Guid.CreateVersion7() },
            input with { Quantity = 3 }
        };

        foreach (var conflictingInput in changed)
        {
            var error = await WhenApplyingWithError(database, conflictingInput);
            ThenFailure(error, "ReceiptIdentityConflict");
        }

        await ThenDurableState(database, item.Id, 7, 1, 1);
    }

    [ExternalIntegrationFact]
    public async Task R05_given_one_receipt_when_two_identical_messages_arrive_concurrently_then_only_one_claim_increments_stock()
    {
        await using var database = await InventoryPostgresDatabase.CreateAsync();
        var item = await GivenStock(database, 5);
        var input = GivenReceipt(item.ProductId, 2);

        var outcomes = await Task.WhenAll(WhenApplying(database, input), WhenApplying(database, input));

        outcomes.ShouldAllBe(outcome => outcome.ResultingStock == 7 && outcome.InventoryItemId == item.Id);
        outcomes.Count(outcome => outcome.WasAlreadyProcessed).ShouldBe(1);
        await ThenDurableState(database, item.Id, 7, 1, 1);
    }

    [ExternalIntegrationFact]
    public async Task R05_given_two_distinct_receipts_when_applied_concurrently_then_both_stock_increments_are_serialized()
    {
        await using var database = await InventoryPostgresDatabase.CreateAsync();
        var item = await GivenStock(database, 5);
        var firstInput = GivenReceipt(item.ProductId, 2);
        var secondInput = GivenReceipt(item.ProductId, 3);

        var outcomes = await Task.WhenAll(WhenApplying(database, firstInput), WhenApplying(database, secondInput));

        outcomes.ShouldAllBe(outcome => !outcome.WasAlreadyProcessed);
        outcomes.Select(outcome => outcome.ResultingStock).Order().ToArray().ShouldBe(new[] { 7, 10 });
        await ThenDurableState(database, item.Id, 10, 2, 2);
    }

    [ExternalIntegrationFact]
    public async Task R07_given_missing_stock_when_receipt_is_retried_after_initialization_then_only_later_attempt_commits()
    {
        await using var database = await InventoryPostgresDatabase.CreateAsync();
        var productId = Guid.CreateVersion7();
        var input = GivenReceipt(productId, 2);

        var error = await WhenApplyingWithError(database, input);
        ThenFailure(error, "InventoryItemNotFound");
        await ThenReceiptAndOutboxCount(database, 0, 0);
        var item = await GivenStock(database, 5, productId);
        var outcome = await WhenApplying(database, input);

        ThenOutcome(outcome, item.Id, 7, false);
        await ThenDurableState(database, item.Id, 7, 1, 1);
    }

    [ExternalIntegrationFact]
    public async Task R07_given_outbox_staging_failure_when_same_receipt_is_retried_then_claim_and_stock_roll_back_before_success()
    {
        await using var database = await InventoryPostgresDatabase.CreateAsync();
        var item = await GivenStock(database, 5);
        var input = GivenReceipt(item.ProductId, 2);
        await using var context = database.CreateContext();

        var error = await Record.ExceptionAsync(() => new PostgresInventoryGoodsReceiptStore(
            context, Substitute.For<IDomainEventDispatcher>()).ApplyAndStageAsync(
                input,
                outcome => new InventoryOutboxMessage(
                    new ProductStockIncreasedIntegrationEvent(item.Id, input.ProductId, input.Quantity, outcome.ResultingStock),
                    new IntegrationMessageDelivery(input.ReceiptId, new string('x', 65))),
                CancellationToken.None));
        ThenFailure(error, "ReceiptStorageUnavailable");
        context.ChangeTracker.Entries().ShouldBeEmpty();
        await ThenDurableState(database, item.Id, 5, 0, 0);

        var retry = await WhenApplying(database, input);
        ThenOutcome(retry, item.Id, 7, false);
        await ThenDurableState(database, item.Id, 7, 1, 1);
    }

    [ExternalIntegrationFact]
    public async Task R07_given_stock_near_integer_limit_when_receipt_overflows_then_no_effect_is_committed()
    {
        await using var database = await InventoryPostgresDatabase.CreateAsync();
        var item = await GivenStock(database, int.MaxValue - 1);
        var input = GivenReceipt(item.ProductId, 2);

        var error = await WhenApplyingWithError(database, input);

        ThenFailure(error, "StockOverflow");
        await ThenDurableState(database, item.Id, int.MaxValue - 1, 0, 0);
    }

    private static ApplyGoodsReceiptInput GivenReceipt(Guid productId, int quantity)
        => new(Guid.CreateVersion7(), Guid.CreateVersion7(), productId, quantity);

    private static async Task<InventoryItem> GivenStock(InventoryPostgresDatabase database, int stock, Guid? productId = null)
    {
        var item = new InventoryItem(productId ?? Guid.CreateVersion7(), stock);
        await using var context = database.CreateContext();
        context.InventoryItems.Add(item);
        await context.SaveChangesAsync();
        return item;
    }

    private static async Task GivenOutboxWasRetainedThenRemoved(InventoryPostgresDatabase database, Guid receiptId)
    {
        await using var context = database.CreateContext();
        (await context.OutboxMessages.Where(row => row.Id == receiptId).ExecuteDeleteAsync()).ShouldBe(1);
    }

    private static async Task<ApplyGoodsReceiptOutput> WhenApplying(InventoryPostgresDatabase database, ApplyGoodsReceiptInput input)
    {
        await using var context = database.CreateContext();
        return await new ApplyGoodsReceiptUseCase(new PostgresInventoryGoodsReceiptStore(
            context, Substitute.For<IDomainEventDispatcher>())).ExecuteAsync(input, CancellationToken.None);
    }

    private static async Task<Exception?> WhenApplyingWithError(InventoryPostgresDatabase database, ApplyGoodsReceiptInput input)
        => await Record.ExceptionAsync(() => WhenApplying(database, input));

    private static void ThenOutcome(ApplyGoodsReceiptOutput outcome, Guid itemId, int stock, bool replay)
    {
        outcome.InventoryItemId.ShouldBe(itemId);
        outcome.ResultingStock.ShouldBe(stock);
        outcome.WasAlreadyProcessed.ShouldBe(replay);
    }

    private static void ThenFailure(Exception? error, string code)
        => error.ShouldBeOfType<InventoryGoodsReceiptException>().Code.ShouldBe(code);

    private static async Task ThenReceiptAndOutboxCount(InventoryPostgresDatabase database, int receipts, int outbox)
    {
        await using var context = database.CreateContext();
        (await context.GoodsReceipts.CountAsync()).ShouldBe(receipts);
        (await context.OutboxMessages.CountAsync()).ShouldBe(outbox);
    }

    private static async Task ThenDurableState(InventoryPostgresDatabase database, Guid itemId, int stock, int receipts, int outbox)
    {
        await using var context = database.CreateContext();
        (await context.InventoryItems.Where(item => item.Id == itemId).Select(item => item.Stock).SingleAsync()).ShouldBe(stock);
        (await context.GoodsReceipts.CountAsync(row => row.CompletedAt != null)).ShouldBe(receipts);
        (await context.OutboxMessages.CountAsync()).ShouldBe(outbox);
    }
}
