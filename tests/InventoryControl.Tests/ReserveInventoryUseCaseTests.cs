using InventoryControl.Applications.Reservations;
using InventoryControl.Infrastructure.Applications.Repositories;
using Lab.BuildingBlocks.Integrations;
using NSubstitute;
using Shouldly;

namespace InventoryControl.Tests;

public sealed class ReserveInventoryUseCaseTests
{
    [Fact]
    public Task given_empty_operation_id_when_reserving_then_request_is_rejected_before_side_effects()
    {
        return AssertInvalidAsync(
            new ReserveInventoryInput(Guid.Empty, Guid.CreateVersion7(), 1),
            "OperationIdRequired");
    }

    [Fact]
    public Task given_empty_product_id_when_reserving_then_request_is_rejected_before_side_effects()
    {
        return AssertInvalidAsync(
            new ReserveInventoryInput(Guid.CreateVersion7(), Guid.Empty, 1),
            "ProductIdRequired");
    }

    [Theory]
    [InlineData(0)]
    [InlineData(-1)]
    public Task given_non_positive_quantity_when_reserving_then_request_is_rejected_before_side_effects(int quantity)
    {
        return AssertInvalidAsync(
            new ReserveInventoryInput(Guid.CreateVersion7(), Guid.CreateVersion7(), quantity),
            "QuantityMustBePositive");
    }

    [Fact]
    public async Task given_insufficient_stock_when_reserving_then_business_failure_is_durable_and_not_published()
    {
        // Given
        var repository = new InMemoryInventoryReservationRepository();
        var publisher = Substitute.For<IIntegrationEventPublisher>();
        var productId = Guid.CreateVersion7();
        repository.Seed(Guid.CreateVersion7(), productId, 1);
        var useCase = new ReserveInventoryUseCase(repository, publisher);

        // When
        var result = await useCase.ExecuteAsync(
            new ReserveInventoryInput(Guid.CreateVersion7(), productId, 2),
            CancellationToken.None);

        // Then
        result.IsSuccess.ShouldBeFalse();
        result.FailureReason.ShouldBe("InventoryIsNotEnough");
        result.RemainingStock.ShouldBe(1);
        repository.GetStock(productId).ShouldBe(1);
        await publisher.DidNotReceiveWithAnyArgs().PublishAsync(default!, default!);
    }

    [Fact]
    public async Task given_an_operation_identity_conflict_when_reserving_then_conflict_is_not_published()
    {
        // Given
        var repository = new InMemoryInventoryReservationRepository();
        var publisher = Substitute.For<IIntegrationEventPublisher>();
        var useCase = new ReserveInventoryUseCase(repository, publisher);
        var operationId = Guid.CreateVersion7();
        var productId = Guid.CreateVersion7();
        repository.Seed(Guid.CreateVersion7(), productId, 5);
        await useCase.ExecuteAsync(
            new ReserveInventoryInput(operationId, productId, 2),
            CancellationToken.None);
        publisher.ClearReceivedCalls();

        // When
        var conflict = await useCase.ExecuteAsync(
            new ReserveInventoryInput(operationId, productId, 3),
            CancellationToken.None);

        // Then
        conflict.IsSuccess.ShouldBeFalse();
        conflict.WasAlreadyProcessed.ShouldBeTrue();
        conflict.FailureReason.ShouldBe("OperationIdentityConflict");
        repository.GetStock(productId).ShouldBe(3);
        await publisher.DidNotReceiveWithAnyArgs().PublishAsync(default!, default!);
    }

    [Fact]
    public async Task given_a_transient_store_failure_when_reserving_then_exception_propagates_without_publication()
    {
        // Given
        var repository = Substitute.For<IInventoryReservationRepository>();
        var publisher = Substitute.For<IIntegrationEventPublisher>();
        var expected = new InventoryReservationTransientException(
            "store unavailable",
            new InvalidOperationException("simulated"));
        repository.ReserveAsync(
                Arg.Any<Guid>(),
                Arg.Any<Guid>(),
                Arg.Any<int>(),
                Arg.Any<CancellationToken>())
            .Returns(_ => Task.FromException<InventoryReservationOutcome>(expected));
        var useCase = new ReserveInventoryUseCase(repository, publisher);

        // When
        var actual = await Should.ThrowAsync<InventoryReservationTransientException>(() =>
            useCase.ExecuteAsync(
                new ReserveInventoryInput(Guid.CreateVersion7(), Guid.CreateVersion7(), 1),
                CancellationToken.None));

        // Then
        actual.ShouldBeSameAs(expected);
        await publisher.DidNotReceiveWithAnyArgs().PublishAsync(default!, default!);
    }

    [Fact]
    public async Task given_publication_fails_after_commit_when_replayed_then_stock_is_not_decremented_twice_and_delivery_identity_is_reused()
    {
        // Given
        var repository = new InMemoryInventoryReservationRepository();
        var publisher = new FailFirstRecordingPublisher();
        var useCase = new ReserveInventoryUseCase(repository, publisher);
        var operationId = Guid.CreateVersion7();
        var productId = Guid.CreateVersion7();
        repository.Seed(Guid.CreateVersion7(), productId, 5);
        var input = new ReserveInventoryInput(operationId, productId, 2);

        // When
        await Should.ThrowAsync<InvalidOperationException>(() =>
            useCase.ExecuteAsync(input, CancellationToken.None));
        var replay = await useCase.ExecuteAsync(input, CancellationToken.None);

        // Then
        replay.IsSuccess.ShouldBeTrue();
        replay.WasAlreadyProcessed.ShouldBeTrue();
        repository.GetStock(productId).ShouldBe(3);
        publisher.Deliveries.Count.ShouldBe(2);
        publisher.Deliveries.ShouldAllBe(delivery =>
            delivery.MessageId == operationId && delivery.PartitionKey == productId.ToString("N"));
    }

    private static async Task AssertInvalidAsync(ReserveInventoryInput input, string expectedReason)
    {
        // Given
        var repository = Substitute.For<IInventoryReservationRepository>();
        var publisher = Substitute.For<IIntegrationEventPublisher>();
        var useCase = new ReserveInventoryUseCase(repository, publisher);

        // When
        var result = await useCase.ExecuteAsync(input, CancellationToken.None);

        // Then
        result.IsSuccess.ShouldBeFalse();
        result.FailureReason.ShouldBe(expectedReason);
        result.WasAlreadyProcessed.ShouldBeFalse();
        result.RemainingStock.ShouldBeNull();
        await repository.DidNotReceiveWithAnyArgs().ReserveAsync(default, default, default, default);
        await publisher.DidNotReceiveWithAnyArgs().PublishAsync(default!, default!);
    }

    private sealed class FailFirstRecordingPublisher : IIntegrationEventPublisher
    {
        public List<IntegrationMessageDelivery> Deliveries { get; } = [];

        public Task PublishAsync(IIntegrationEvent integrationEvent)
        {
            return Task.CompletedTask;
        }

        public Task PublishAsync(IIntegrationEvent integrationEvent, IntegrationMessageDelivery delivery)
        {
            this.Deliveries.Add(delivery);
            return this.Deliveries.Count == 1
                ? Task.FromException(new InvalidOperationException("simulated publication failure"))
                : Task.CompletedTask;
        }
    }
}
