using Lab.BoundedContextContracts.Inventory.Interactions;
using Lab.BoundedContextContracts.Orders.IntegrationEvents;
using Lab.BuildingBlocks.Integrations;
using NSubstitute;
using SaleOrders.Applications.Gateways;
using SaleOrders.Applications.Repositories;
using SaleOrders.Applications.UseCases;
using SaleOrders.Domains;
using Shouldly;

namespace SaleOrders.Tests;

/// <summary>Broker-free GWT coverage for the high-risk PlaceOrder flow.</summary>
public sealed class PlaceOrderTests
{
    /// <summary>Successful reservation atomically commits the OrderPlaced message.</summary>
    [Fact]
    public async Task given_inventory_is_reserved_when_order_is_placed_then_order_and_outbox_message_are_committed()
    {
        // Given
        var operationId = Guid.CreateVersion7();
        var productId = Guid.CreateVersion7();
        var input = new PlaceOrderInput(
            operationId,
            new DateTime(2026, 7, 14, 0, 0, 0, DateTimeKind.Utc),
            120m,
            productId,
            "Architecture Lab",
            3);
        var gateway = Substitute.For<IInventoryGateway>();
        gateway.ReserveAsync(
                   Arg.Is<ReserveInventoryRequestContract>(request =>
                       request.OperationId == operationId &&
                       request.ProductId == productId && request.Quantity == 3),
                   Arg.Any<CancellationToken>())
               .Returns(new ReserveInventoryResponseContract { Result = true });
        var committer = Substitute.For<IOrderEventCommitter>();
        var useCase = new PlaceOrderUseCase(committer, gateway);

        // When
        var result = await useCase.ExecuteAsync(input, CancellationToken.None);

        // Then
        result.IsSuccess.ShouldBeTrue();
        result.Value.ShouldNotBeNull();
        await committer.Received(1).CommitAsync(
            Arg.Is<Order>(order =>
                order.Id == result.Value.OrderId &&
                order.ProductId == productId &&
                order.Quantity == 3),
            Arg.Is<IReadOnlyCollection<IIntegrationEvent>>(events =>
                IsExpectedOrderPlaced(events, result.Value.OrderId, productId, 3)),
            Arg.Any<CancellationToken>());
    }

    /// <summary>Reservation failure must not persist an order or enqueue a success event.</summary>
    [Fact]
    public async Task given_inventory_is_insufficient_when_order_is_placed_then_commit_is_skipped()
    {
        // Given
        var operationId = Guid.CreateVersion7();
        var productId = Guid.CreateVersion7();
        var input = new PlaceOrderInput(operationId, DateTime.UtcNow, 120m, productId, "Architecture Lab", 3);
        var gateway = Substitute.For<IInventoryGateway>();
        gateway.ReserveAsync(
                   Arg.Any<ReserveInventoryRequestContract>(),
                   Arg.Any<CancellationToken>())
               .Returns(new ReserveInventoryResponseContract { Result = false });
        var committer = Substitute.For<IOrderEventCommitter>();
        var useCase = new PlaceOrderUseCase(committer, gateway);

        // When
        var result = await useCase.ExecuteAsync(input, CancellationToken.None);

        // Then
        result.IsSuccess.ShouldBeFalse();
        result.ErrorMessage.ShouldBe("Inventory is not enough.");
        result.Value.ShouldBeNull();
        await committer.DidNotReceiveWithAnyArgs().CommitAsync(default!, default!, default);
    }

    private static bool IsExpectedOrderPlaced(
        IReadOnlyCollection<IIntegrationEvent> events,
        Guid orderId,
        Guid productId,
        int quantity)
    {
        var placed = events.SingleOrDefault() as OrderPlaced;
        return events.Count == 1 &&
               placed?.OrderId == orderId &&
               placed.ProductId == productId &&
               placed.Quantity == quantity;
    }
}
