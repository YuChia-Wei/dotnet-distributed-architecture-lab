using InventoryControl.Applications.Outbox;
using InventoryControl.Applications.Reservations;
using InventoryControl.Domains;
using InventoryControl.Infrastructure.Applications.Repositories;
using InventoryControl.Infrastructure.Persistence;
using Lab.BoundedContextContracts.Inventory.IntegrationEvents;
using Lab.BuildingBlocks.Integrations;
using Microsoft.EntityFrameworkCore;
using Shouldly;

namespace InventoryControl.Tests;

/// <summary>AC4: durable operation identity, concurrency and rollback through the actual PostgreSQL adapter.</summary>
public sealed class PostgresInventoryReservationRepositoryTests
{
    [ExternalIntegrationFact]
    [Trait("Category", "ExternalIntegration")]
    public async Task given_stock_for_only_one_request_when_two_reservations_run_concurrently_then_stock_and_outcomes_are_atomic()
    {
        await using var database = await InventoryPostgresDatabase.CreateAsync();
        var item = await GivenStock(database, 3);
        var outcomes = await WhenReservingConcurrently(database, item.ProductId, 2, Guid.CreateVersion7(), Guid.CreateVersion7());
        ThenOnlyOneReservationShouldSucceed(outcomes, 1);
        await ThenDurableStateShouldBe(database, item.Id, 1, 2, 1, 1);
    }

    [ExternalIntegrationFact]
    public async Task given_one_operation_when_duplicate_requests_run_concurrently_then_the_outcome_and_message_are_replayed_once()
    {
        await using var database = await InventoryPostgresDatabase.CreateAsync();
        var item = await GivenStock(database, 5);
        var operationId = Guid.CreateVersion7();
        var outcomes = await WhenReservingConcurrently(database, item.ProductId, 2, operationId, operationId);
        ThenDuplicateShouldReplay(outcomes, 3);
        await ThenDurableStateShouldBe(database, item.Id, 3, 1, 1, 1);
    }

    [ExternalIntegrationFact]
    public async Task given_a_completed_operation_when_payload_changes_then_the_conflict_preserves_the_original_state()
    {
        await using var database = await InventoryPostgresDatabase.CreateAsync();
        var item = await GivenStock(database, 5);
        var operationId = Guid.CreateVersion7();
        await GivenCompletedReservation(database, operationId, item.ProductId, 2);
        var outcome = await WhenReserving(database, operationId, item.ProductId, 3);
        ThenFailureShouldBe(outcome, "OperationIdentityConflict", true);
        await ThenDurableStateShouldBe(database, item.Id, 3, 1, 1, 1);
    }

    [ExternalIntegrationFact]
    public async Task given_a_failed_operation_when_stock_changes_then_replay_preserves_the_terminal_outcome()
    {
        await using var database = await InventoryPostgresDatabase.CreateAsync();
        var item = await GivenStock(database, 1);
        var operationId = Guid.CreateVersion7();
        await GivenCompletedReservation(database, operationId, item.ProductId, 2);
        await GivenStockChanged(database, item.Id, 5);
        var outcome = await WhenReserving(database, operationId, item.ProductId, 2);
        ThenFailureShouldBe(outcome, "InventoryIsNotEnough", true);
        outcome.RemainingStock.ShouldBe(1);
        await ThenDurableStateShouldBe(database, item.Id, 5, 1, 0, 0);
    }

    [ExternalIntegrationFact]
    public async Task given_invalid_outbox_metadata_when_reservation_staging_fails_then_stock_operation_and_message_roll_back()
    {
        await using var database = await InventoryPostgresDatabase.CreateAsync();
        var item = await GivenStock(database, 5);
        var operationId = Guid.CreateVersion7();
        await using var context = database.CreateContext();
        var error = await WhenStagingInvalidReservation(context, operationId, item.ProductId, 2);
        ThenRollbackShouldCleanTrackedState(context, error);
        await ThenDurableStateShouldBe(database, item.Id, 5, 0, 0, 0);
    }

    [ExternalIntegrationFact]
    public async Task given_a_rolled_back_scope_when_the_operation_is_retried_then_only_the_retry_commits()
    {
        await using var database = await InventoryPostgresDatabase.CreateAsync();
        var item = await GivenStock(database, 5);
        var operationId = Guid.CreateVersion7();
        await using var context = database.CreateContext();
        await GivenRolledBackReservation(context, operationId, item.ProductId, 2);
        var outcome = await WhenReserving(context, operationId, item.ProductId, 2);
        ThenReservationShouldSucceed(outcome, 3);
        await ThenDurableStateShouldBe(database, item.Id, 3, 1, 1, 1);
    }

    private static async Task<InventoryItem> GivenStock(InventoryPostgresDatabase database, int stock)
    {
        var item = new InventoryItem(Guid.CreateVersion7(), stock);
        await using var context = database.CreateContext();
        context.InventoryItems.Add(item);
        await context.SaveChangesAsync();
        return item;
    }

    private static async Task GivenStockChanged(InventoryPostgresDatabase database, Guid itemId, int stock)
    {
        await using var context = database.CreateContext();
        await context.InventoryItems.Where(item => item.Id == itemId).ExecuteUpdateAsync(setters => setters.SetProperty(item => item.Stock, stock));
    }

    private static async Task GivenCompletedReservation(InventoryPostgresDatabase database, Guid operationId, Guid productId, int quantity)
        => await WhenReserving(database, operationId, productId, quantity);

    private static async Task GivenRolledBackReservation(InventoryDbContext context, Guid operationId, Guid productId, int quantity)
    {
        var error = await WhenStagingInvalidReservation(context, operationId, productId, quantity);
        error.ShouldBeOfType<InventoryReservationTransientException>();
    }

    private static async Task<ReserveInventoryOutput[]> WhenReservingConcurrently(InventoryPostgresDatabase database, Guid productId,
        int quantity, Guid firstOperationId, Guid secondOperationId)
        => await Task.WhenAll(WhenReserving(database, firstOperationId, productId, quantity), WhenReserving(database, secondOperationId, productId, quantity));

    private static async Task<ReserveInventoryOutput> WhenReserving(InventoryPostgresDatabase database, Guid operationId, Guid productId, int quantity)
    {
        await using var context = database.CreateContext();
        return await WhenReserving(context, operationId, productId, quantity);
    }

    private static Task<ReserveInventoryOutput> WhenReserving(InventoryDbContext context, Guid operationId, Guid productId, int quantity)
        => new ReserveInventoryUseCase(new PostgresInventoryReservationRepository(context))
            .ExecuteAsync(new ReserveInventoryInput(operationId, productId, quantity), CancellationToken.None);

    private static async Task<Exception?> WhenStagingInvalidReservation(InventoryDbContext context, Guid operationId, Guid productId, int quantity)
        => await Record.ExceptionAsync(() => new PostgresInventoryReservationRepository(context).ReserveAndStageAsync(operationId, productId, quantity,
            outcome => new InventoryOutboxMessage(
                new ProductStockDecreasedIntegrationEvent(outcome.InventoryItemId!.Value, productId, quantity, outcome.RemainingStock!.Value),
                new IntegrationMessageDelivery(operationId, new string('x', 65))), CancellationToken.None));

    private static void ThenOnlyOneReservationShouldSucceed(ReserveInventoryOutput[] outcomes, int remainingStock)
    {
        outcomes.Count(outcome => outcome.IsSuccess).ShouldBe(1);
        outcomes.Count(outcome => outcome.FailureReason == "InventoryIsNotEnough").ShouldBe(1);
        outcomes.ShouldAllBe(outcome => outcome.RemainingStock == remainingStock);
    }

    private static void ThenDuplicateShouldReplay(ReserveInventoryOutput[] outcomes, int remainingStock)
    {
        outcomes.ShouldAllBe(outcome => outcome.IsSuccess && outcome.RemainingStock == remainingStock);
        outcomes.Count(outcome => outcome.WasAlreadyProcessed).ShouldBe(1);
    }

    private static void ThenFailureShouldBe(ReserveInventoryOutput outcome, string reason, bool replayed)
    {
        outcome.IsSuccess.ShouldBeFalse();
        outcome.FailureReason.ShouldBe(reason);
        outcome.WasAlreadyProcessed.ShouldBe(replayed);
    }

    private static void ThenRollbackShouldCleanTrackedState(InventoryDbContext context, Exception? error)
    {
        error.ShouldBeOfType<InventoryReservationTransientException>();
        context.ChangeTracker.Entries().ShouldBeEmpty();
    }

    private static void ThenReservationShouldSucceed(ReserveInventoryOutput outcome, int remainingStock)
    {
        outcome.IsSuccess.ShouldBeTrue();
        outcome.WasAlreadyProcessed.ShouldBeFalse();
        outcome.RemainingStock.ShouldBe(remainingStock);
    }

    private static async Task ThenDurableStateShouldBe(InventoryPostgresDatabase database, Guid itemId, int stock, int completed, int successes, int messages)
    {
        await using var context = database.CreateContext();
        (await context.InventoryItems.Where(item => item.Id == itemId).Select(item => item.Stock).SingleAsync()).ShouldBe(stock);
        (await context.ReservationOperations.CountAsync(operation => operation.CompletedAt != null)).ShouldBe(completed);
        (await context.ReservationOperations.CountAsync(operation => operation.IsSuccess == true)).ShouldBe(successes);
        (await context.OutboxMessages.CountAsync()).ShouldBe(messages);
    }
}
