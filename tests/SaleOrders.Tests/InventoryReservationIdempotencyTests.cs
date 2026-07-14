using InventoryControl.Applications.Reservations;
using InventoryControl.Infrastructure.Applications.Repositories;
using InventoryControl.Infrastructure.Messaging;
using Lab.BuildingBlocks.Integrations;
using NSubstitute;
using Shouldly;
using Wolverine;

namespace SaleOrders.Tests;

public sealed class InventoryReservationIdempotencyTests
{
    [Fact]
    public async Task given_a_completed_operation_when_it_is_replayed_then_stock_is_decremented_once()
    {
        var repository = new InMemoryInventoryReservationRepository();
        var operationId = Guid.CreateVersion7();
        var productId = Guid.CreateVersion7();
        repository.Seed(Guid.CreateVersion7(), productId, 5);

        var first = await repository.ReserveAsync(operationId, productId, 2, CancellationToken.None);
        var replay = await repository.ReserveAsync(operationId, productId, 2, CancellationToken.None);

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

        await repository.ReserveAsync(operationId, productId, 2, CancellationToken.None);
        var conflict = await repository.ReserveAsync(operationId, productId, 3, CancellationToken.None);

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

        var first = await repository.ReserveAsync(operationId, productId, 2, CancellationToken.None);
        repository.Seed(Guid.CreateVersion7(), productId, 5);
        var replay = await repository.ReserveAsync(operationId, productId, 2, CancellationToken.None);

        first.FailureReason.ShouldBe("InventoryItemNotFound");
        replay.FailureReason.ShouldBe("InventoryItemNotFound");
        replay.WasAlreadyProcessed.ShouldBeTrue();
        repository.GetStock(productId).ShouldBe(5);
    }

    [Fact]
    public async Task given_a_successful_replay_when_the_event_is_republished_then_delivery_identity_is_stable()
    {
        var repository = new InMemoryInventoryReservationRepository();
        var publisher = Substitute.For<IIntegrationEventPublisher>();
        var useCase = new ReserveInventoryUseCase(repository, publisher);
        var operationId = Guid.CreateVersion7();
        var productId = Guid.CreateVersion7();
        repository.Seed(Guid.CreateVersion7(), productId, 5);
        var input = new ReserveInventoryInput(operationId, productId, 2);

        await useCase.ExecuteAsync(input, CancellationToken.None);
        await useCase.ExecuteAsync(input, CancellationToken.None);

        repository.GetStock(productId).ShouldBe(3);
        await publisher.Received(2).PublishAsync(
            Arg.Any<IIntegrationEvent>(),
            Arg.Is<IntegrationMessageDelivery>(delivery =>
                delivery.MessageId == operationId && delivery.PartitionKey == productId.ToString("N")));
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

        await Should.ThrowAsync<OperationCanceledException>(() =>
            repository.ReserveAsync(operationId, productId, 2, cancellation.Token));

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
