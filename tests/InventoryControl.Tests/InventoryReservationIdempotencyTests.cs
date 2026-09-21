using InventoryControl.Applications.Reservations;
using InventoryControl.Infrastructure.Applications.Repositories;
using InventoryControl.Infrastructure.Messaging;
using Shouldly;
using Wolverine;

namespace InventoryControl.Tests;

public sealed class InventoryReservationIdempotencyTests
{
    [Fact]
    public async Task given_a_completed_operation_when_it_is_replayed_then_stock_is_decremented_once()
    {
        var repository = new InMemoryInventoryReservationRepository();
        var operationId = Guid.CreateVersion7();
        var productId = Guid.CreateVersion7();
        repository.Seed(Guid.CreateVersion7(), productId, 5);
        var useCase = new ReserveInventoryUseCase(repository);

        var first = await useCase.ExecuteAsync(
            new ReserveInventoryInput(operationId, productId, 2), CancellationToken.None);
        var replay = await useCase.ExecuteAsync(
            new ReserveInventoryInput(operationId, productId, 2), CancellationToken.None);

        first.WasAlreadyProcessed.ShouldBeFalse();
        replay.WasAlreadyProcessed.ShouldBeTrue();
        replay.IsSuccess.ShouldBeTrue();
        replay.RemainingStock.ShouldBe(3);
        repository.GetStock(productId).ShouldBe(3);
    }

    [Fact]
    public async Task given_an_operation_identity_when_payload_changes_then_the_conflict_is_terminal()
    {
        var repository = new InMemoryInventoryReservationRepository();
        var operationId = Guid.CreateVersion7();
        var productId = Guid.CreateVersion7();
        repository.Seed(Guid.CreateVersion7(), productId, 5);
        var useCase = new ReserveInventoryUseCase(repository);

        await useCase.ExecuteAsync(
            new ReserveInventoryInput(operationId, productId, 2), CancellationToken.None);
        var conflict = await useCase.ExecuteAsync(
            new ReserveInventoryInput(operationId, productId, 3), CancellationToken.None);

        conflict.IsSuccess.ShouldBeFalse();
        conflict.WasAlreadyProcessed.ShouldBeTrue();
        conflict.FailureReason.ShouldBe("OperationIdentityConflict");
        repository.GetStock(productId).ShouldBe(3);
    }

    [Fact]
    public async Task given_a_terminal_failure_when_stock_changes_then_replay_preserves_the_original_outcome()
    {
        var repository = new InMemoryInventoryReservationRepository();
        var operationId = Guid.CreateVersion7();
        var productId = Guid.CreateVersion7();
        var useCase = new ReserveInventoryUseCase(repository);

        var first = await useCase.ExecuteAsync(
            new ReserveInventoryInput(operationId, productId, 2), CancellationToken.None);
        repository.Seed(Guid.CreateVersion7(), productId, 5);
        var replay = await useCase.ExecuteAsync(
            new ReserveInventoryInput(operationId, productId, 2), CancellationToken.None);

        first.FailureReason.ShouldBe("InventoryItemNotFound");
        replay.FailureReason.ShouldBe("InventoryItemNotFound");
        replay.WasAlreadyProcessed.ShouldBeTrue();
        repository.GetStock(productId).ShouldBe(5);
    }

    [Fact]
    public async Task given_a_successful_replay_when_the_event_is_staged_then_delivery_identity_is_stable()
    {
        var repository = new InMemoryInventoryReservationRepository();
        var useCase = new ReserveInventoryUseCase(repository);
        var operationId = Guid.CreateVersion7();
        var productId = Guid.CreateVersion7();
        repository.Seed(Guid.CreateVersion7(), productId, 5);
        var input = new ReserveInventoryInput(operationId, productId, 2);

        await useCase.ExecuteAsync(input, CancellationToken.None);
        await useCase.ExecuteAsync(input, CancellationToken.None);

        repository.GetStock(productId).ShouldBe(3);
        var staged = repository.GetStagedMessages().ShouldHaveSingleItem();
        staged.Delivery.MessageId.ShouldBe(operationId);
        staged.Delivery.PartitionKey.ShouldBe(productId.ToString("N"));
    }

    /// <summary>R02：已完成的成功預留只重播結果，不得再次呼叫成功訊息 factory。</summary>
    [Fact]
    public async Task given_a_successful_reservation_when_replayed_then_the_message_factory_is_not_called()
    {
        var input = new ReserveInventoryInput(Guid.CreateVersion7(), Guid.CreateVersion7(), 2);
        var repository = await GivenCompletedSuccessfulReservation(input, initialStock: 5);

        var (outcome, error, factoryCalls) = await WhenReplayingWithUnexpectedMessageFactory(repository, input);

        ThenReplayShouldReturnWithoutCallingFactory(repository, input, outcome, error, factoryCalls, remainingStock: 3);
    }

    private static async Task<InMemoryInventoryReservationRepository> GivenCompletedSuccessfulReservation(
        ReserveInventoryInput input, int initialStock)
    {
        var repository = new InMemoryInventoryReservationRepository();
        repository.Seed(Guid.CreateVersion7(), input.ProductId, initialStock);
        var result = await new ReserveInventoryUseCase(repository).ExecuteAsync(input, TestContext.Current.CancellationToken);
        result.IsSuccess.ShouldBeTrue();
        return repository;
    }

    private static async Task<(InventoryReservationOutcome? Outcome, Exception? Error, int FactoryCalls)>
        WhenReplayingWithUnexpectedMessageFactory(InMemoryInventoryReservationRepository repository, ReserveInventoryInput input)
    {
        InventoryReservationOutcome? outcome = null;
        var factoryCalls = 0;
        var error = await Record.ExceptionAsync(async () =>
        {
            outcome = await repository.ReserveAndStageAsync(input.OperationId, input.ProductId, input.Quantity,
                _ =>
                {
                    factoryCalls++;
                    throw new InvalidOperationException("A replay must not construct another message.");
                }, TestContext.Current.CancellationToken);
        });
        return (outcome, error, factoryCalls);
    }

    private static void ThenReplayShouldReturnWithoutCallingFactory(InMemoryInventoryReservationRepository repository,
        ReserveInventoryInput input, InventoryReservationOutcome? outcome, Exception? error, int factoryCalls, int remainingStock)
    {
        factoryCalls.ShouldBe(0);
        error.ShouldBeNull();
        outcome.ShouldNotBeNull();
        outcome.OperationId.ShouldBe(input.OperationId);
        outcome.IsSuccess.ShouldBeTrue();
        outcome.WasAlreadyProcessed.ShouldBeTrue();
        outcome.RemainingStock.ShouldBe(remainingStock);
        repository.GetStock(input.ProductId).ShouldBe(remainingStock);
        repository.GetStagedMessages().ShouldHaveSingleItem().Delivery.MessageId.ShouldBe(input.OperationId);
    }

    [Fact]
    public async Task given_cancellation_before_reservation_when_executed_then_state_is_not_mutated()
    {
        var repository = new InMemoryInventoryReservationRepository();
        var operationId = Guid.CreateVersion7();
        var productId = Guid.CreateVersion7();
        repository.Seed(Guid.CreateVersion7(), productId, 5);
        using var cancellation = new CancellationTokenSource();
        cancellation.Cancel();
        var useCase = new ReserveInventoryUseCase(repository);

        await Should.ThrowAsync<OperationCanceledException>(() =>
            useCase.ExecuteAsync(
                new ReserveInventoryInput(operationId, productId, 2), cancellation.Token));

        repository.GetStock(productId).ShouldBe(5);
    }

    [Fact]
    public void reservation_failure_policy_has_bounded_cooldowns_and_terminal_routing_configuration()
    {
        InventoryReservationFailurePolicy.RetryDelays.ShouldBe(
        [
            TimeSpan.FromMilliseconds(100),
            TimeSpan.FromMilliseconds(500),
            TimeSpan.FromSeconds(2)
        ]);

        Should.NotThrow(() => InventoryReservationFailurePolicy.Configure(new WolverineOptions()));
    }
}
