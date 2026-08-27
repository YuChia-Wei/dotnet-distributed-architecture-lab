using InventoryControl.Applications.Reservations;
using InventoryControl.Infrastructure.Applications.Repositories;
using Lab.BoundedContextContracts.Inventory.IntegrationEvents;
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
    public async Task given_insufficient_stock_when_reserving_then_failure_is_committed_without_an_outbox_message()
    {
        // Given
        var repository = new InMemoryInventoryReservationRepository();
        var productId = Guid.CreateVersion7();
        repository.Seed(Guid.CreateVersion7(), productId, 1);
        var useCase = new ReserveInventoryUseCase(repository);

        // When
        var result = await useCase.ExecuteAsync(
            new ReserveInventoryInput(Guid.CreateVersion7(), productId, 2),
            CancellationToken.None);

        // Then
        result.IsSuccess.ShouldBeFalse();
        result.FailureReason.ShouldBe("InventoryIsNotEnough");
        result.RemainingStock.ShouldBe(1);
        repository.GetStock(productId).ShouldBe(1);
        repository.GetStagedMessages().ShouldBeEmpty();
    }

    [Fact]
    public async Task given_an_operation_identity_conflict_when_reserving_then_only_the_original_outbox_message_remains()
    {
        // Given
        var repository = new InMemoryInventoryReservationRepository();
        var useCase = new ReserveInventoryUseCase(repository);
        var operationId = Guid.CreateVersion7();
        var productId = Guid.CreateVersion7();
        repository.Seed(Guid.CreateVersion7(), productId, 5);
        await useCase.ExecuteAsync(
            new ReserveInventoryInput(operationId, productId, 2),
            CancellationToken.None);

        // When
        var conflict = await useCase.ExecuteAsync(
            new ReserveInventoryInput(operationId, productId, 3),
            CancellationToken.None);

        // Then
        conflict.IsSuccess.ShouldBeFalse();
        conflict.WasAlreadyProcessed.ShouldBeTrue();
        conflict.FailureReason.ShouldBe("OperationIdentityConflict");
        repository.GetStock(productId).ShouldBe(3);
        repository.GetStagedMessages().Count.ShouldBe(1);
    }

    [Fact]
    public async Task given_a_transient_store_failure_when_reserving_then_exception_propagates_without_commit()
    {
        // Given
        var transaction = Substitute.For<IInventoryReservationTransaction>();
        var factory = Substitute.For<IInventoryReservationTransactionFactory>();
        factory.BeginAsync(Arg.Any<CancellationToken>()).Returns(Task.FromResult(transaction));
        var expected = new InventoryReservationTransientException(
            "store unavailable",
            new InvalidOperationException("simulated"));
        transaction.ReserveAsync(
                Arg.Any<Guid>(),
                Arg.Any<Guid>(),
                Arg.Any<int>(),
                Arg.Any<CancellationToken>())
            .Returns(_ => Task.FromException<InventoryReservationOutcome>(expected));
        var useCase = new ReserveInventoryUseCase(factory);

        // When
        var actual = await Should.ThrowAsync<InventoryReservationTransientException>(() =>
            useCase.ExecuteAsync(
                new ReserveInventoryInput(Guid.CreateVersion7(), Guid.CreateVersion7(), 1),
                CancellationToken.None));

        // Then
        actual.ShouldBeSameAs(expected);
        await transaction.DidNotReceiveWithAnyArgs().StageAsync(default!, default!, default);
        await transaction.DidNotReceiveWithAnyArgs().CommitAsync(default);
    }

    [Fact]
    public async Task given_sufficient_stock_when_reserving_then_state_and_outbox_commit_with_stable_delivery_identity()
    {
        // Given
        var repository = new InMemoryInventoryReservationRepository();
        var operationId = Guid.CreateVersion7();
        var productId = Guid.CreateVersion7();
        repository.Seed(Guid.CreateVersion7(), productId, 5);
        var useCase = new ReserveInventoryUseCase(repository);

        // When
        var result = await useCase.ExecuteAsync(
            new ReserveInventoryInput(operationId, productId, 2),
            CancellationToken.None);

        // Then
        result.IsSuccess.ShouldBeTrue();
        repository.GetStock(productId).ShouldBe(3);
        var staged = repository.GetStagedMessages().ShouldHaveSingleItem();
        staged.IntegrationEvent.ShouldBeOfType<ProductStockDecreasedIntegrationEvent>();
        staged.Delivery.MessageId.ShouldBe(operationId);
        staged.Delivery.PartitionKey.ShouldBe(productId.ToString("N"));
    }

    [Fact]
    public async Task given_a_successful_replay_when_committed_then_stock_and_outbox_are_not_duplicated()
    {
        // Given
        var repository = new InMemoryInventoryReservationRepository();
        var operationId = Guid.CreateVersion7();
        var productId = Guid.CreateVersion7();
        repository.Seed(Guid.CreateVersion7(), productId, 5);
        var useCase = new ReserveInventoryUseCase(repository);
        var input = new ReserveInventoryInput(operationId, productId, 2);
        await useCase.ExecuteAsync(input, CancellationToken.None);

        // When
        var replay = await useCase.ExecuteAsync(input, CancellationToken.None);

        // Then
        replay.IsSuccess.ShouldBeTrue();
        replay.WasAlreadyProcessed.ShouldBeTrue();
        repository.GetStock(productId).ShouldBe(3);
        repository.GetStagedMessages().ShouldHaveSingleItem().Delivery.MessageId.ShouldBe(operationId);
    }

    [Fact]
    public async Task given_outbox_staging_fails_when_reserving_then_the_transaction_is_not_committed()
    {
        // Given
        var operationId = Guid.CreateVersion7();
        var productId = Guid.CreateVersion7();
        var transaction = Substitute.For<IInventoryReservationTransaction>();
        var factory = Substitute.For<IInventoryReservationTransactionFactory>();
        factory.BeginAsync(Arg.Any<CancellationToken>()).Returns(Task.FromResult(transaction));
        transaction.ReserveAsync(operationId, productId, 2, Arg.Any<CancellationToken>())
            .Returns(new InventoryReservationOutcome(
                operationId,
                productId,
                2,
                Guid.CreateVersion7(),
                true,
                3,
                null,
                false));
        transaction.StageAsync(
                Arg.Any<IIntegrationEvent>(),
                Arg.Any<IntegrationMessageDelivery>(),
                Arg.Any<CancellationToken>())
            .Returns(_ => Task.FromException(new InvalidOperationException("simulated outbox failure")));
        var useCase = new ReserveInventoryUseCase(factory);

        // When
        await Should.ThrowAsync<InvalidOperationException>(() =>
            useCase.ExecuteAsync(
                new ReserveInventoryInput(operationId, productId, 2),
                CancellationToken.None));

        // Then
        await transaction.DidNotReceiveWithAnyArgs().CommitAsync(default);
    }

    private static async Task AssertInvalidAsync(ReserveInventoryInput input, string expectedReason)
    {
        // Given
        var factory = Substitute.For<IInventoryReservationTransactionFactory>();
        var useCase = new ReserveInventoryUseCase(factory);

        // When
        var result = await useCase.ExecuteAsync(input, CancellationToken.None);

        // Then
        result.IsSuccess.ShouldBeFalse();
        result.FailureReason.ShouldBe(expectedReason);
        result.WasAlreadyProcessed.ShouldBeFalse();
        result.RemainingStock.ShouldBeNull();
        await factory.DidNotReceiveWithAnyArgs().BeginAsync(default);
    }
}
