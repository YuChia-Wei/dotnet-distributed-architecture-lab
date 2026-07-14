using InventoryControl.Applications.Repositories;
using InventoryControl.Applications.Queries;
using InventoryControl.Applications.UseCases;
using InventoryControl.Domains;
using Lab.BoundedContextContracts.Inventory.IntegrationEvents;
using Lab.BuildingBlocks.Integrations;
using NSubstitute;
using Shouldly;

namespace SaleOrders.Tests;

/// <summary>Broker-free GWT coverage for high-risk Inventory mutations.</summary>
public sealed class InventoryStockUseCaseTests
{
    /// <summary>Available stock is persisted and announced after a successful decrease.</summary>
    [Fact]
    public async Task given_sufficient_stock_when_stock_is_decreased_then_state_is_saved_and_event_is_published()
    {
        // Given
        var productId = Guid.CreateVersion7();
        var item = new InventoryItem(productId, 10);
        var (repository, queries) = RepositoriesReturning(productId, item);
        var publisher = PublisherAcceptingMessages();
        var useCase = new DecreaseStockUseCase(repository, queries, publisher);

        // When
        var result = await useCase.ExecuteAsync(new DecreaseStockInput(productId, 4), CancellationToken.None);

        // Then
        result.IsSuccess.ShouldBeTrue();
        result.Value.ShouldNotBeNull();
        result.Value.CurrentStock.ShouldBe(6);
        item.Stock.ShouldBe(6);
        await repository.Received(1).SaveAsync(item, Arg.Any<CancellationToken>());
        await publisher.Received(1).PublishAsync(
            Arg.Is<IIntegrationEvent>(message => IsExpectedDecrease(message, item.Id, productId, 4, 6)));
    }

    /// <summary>Insufficient stock is a business failure without persistence or publication.</summary>
    [Fact]
    public async Task given_insufficient_stock_when_stock_is_decreased_then_state_and_side_effects_are_unchanged()
    {
        // Given
        var productId = Guid.CreateVersion7();
        var item = new InventoryItem(productId, 2);
        var (repository, queries) = RepositoriesReturning(productId, item);
        var publisher = Substitute.For<IIntegrationEventPublisher>();
        var useCase = new DecreaseStockUseCase(repository, queries, publisher);

        // When
        var result = await useCase.ExecuteAsync(new DecreaseStockInput(productId, 3), CancellationToken.None);

        // Then
        result.IsSuccess.ShouldBeFalse();
        result.ErrorMessage.ShouldBe("Available stock is not enough.");
        item.Stock.ShouldBe(2);
        item.DomainEvents.ShouldBeEmpty();
        await repository.DidNotReceiveWithAnyArgs().SaveAsync(default!, default);
        await publisher.DidNotReceiveWithAnyArgs().PublishAsync(default!);
    }

    /// <summary>A missing item suppresses persistence and the stock-decreased success message.</summary>
    [Fact]
    public async Task given_inventory_item_is_missing_when_stock_is_decreased_then_failure_has_no_side_effects()
    {
        // Given
        var productId = Guid.CreateVersion7();
        var (repository, queries) = RepositoriesReturning(productId, null);
        var publisher = Substitute.For<IIntegrationEventPublisher>();
        var useCase = new DecreaseStockUseCase(repository, queries, publisher);

        // When
        var result = await useCase.ExecuteAsync(new DecreaseStockInput(productId, 1), CancellationToken.None);

        // Then
        result.IsSuccess.ShouldBeFalse();
        result.ErrorMessage.ShouldBe("InventoryItemNotFound");
        await repository.DidNotReceiveWithAnyArgs().SaveAsync(default!, default);
        await publisher.DidNotReceiveWithAnyArgs().PublishAsync(default!);
    }

    /// <summary>Increasing stock persists the aggregate and publishes the resulting current stock.</summary>
    [Fact]
    public async Task given_inventory_item_exists_when_stock_is_increased_then_state_is_saved_and_event_is_published()
    {
        // Given
        var productId = Guid.CreateVersion7();
        var item = new InventoryItem(productId, 5);
        var (repository, queries) = RepositoriesReturning(productId, item);
        var publisher = PublisherAcceptingMessages();
        var useCase = new IncreaseStockUseCase(repository, queries, publisher);

        // When
        var result = await useCase.ExecuteAsync(new IncreaseStockInput(productId, 4), CancellationToken.None);

        // Then
        result.IsSuccess.ShouldBeTrue();
        result.Value!.CurrentStock.ShouldBe(9);
        await repository.Received(1).SaveAsync(item, Arg.Any<CancellationToken>());
        await publisher.Received(1).PublishAsync(
            Arg.Is<IIntegrationEvent>(message => IsExpectedIncrease(message, productId, 4, 9)));
    }

    /// <summary>Restocking persists the aggregate and publishes the returned quantity.</summary>
    [Fact]
    public async Task given_inventory_item_exists_when_stock_is_restocked_then_state_is_saved_and_event_is_published()
    {
        // Given
        var productId = Guid.CreateVersion7();
        var item = new InventoryItem(productId, 5);
        var (repository, queries) = RepositoriesReturning(productId, item);
        var publisher = PublisherAcceptingMessages();
        var useCase = new RestockUseCase(repository, queries, publisher);

        // When
        var result = await useCase.ExecuteAsync(new RestockInput(productId, 2), CancellationToken.None);

        // Then
        result.IsSuccess.ShouldBeTrue();
        result.Value!.CurrentStock.ShouldBe(7);
        await repository.Received(1).SaveAsync(item, Arg.Any<CancellationToken>());
        await publisher.Received(1).PublishAsync(
            Arg.Is<IIntegrationEvent>(message => IsExpectedReturn(message, productId, 2, 7)));
    }

    private static (IInventoryItemDomainRepository Repository, IInventoryItemQueryRepository Queries) RepositoriesReturning(
        Guid productId,
        InventoryItem? item)
    {
        var repository = Substitute.For<IInventoryItemDomainRepository>();
        var queries = Substitute.For<IInventoryItemQueryRepository>();
        if (item is not null)
        {
            queries.FindByProductIdAsync(productId, Arg.Any<CancellationToken>())
                .Returns(new InventoryItemReadModel(item.Id, item.ProductId, item.Stock));
            repository.FindByIdAsync(item.Id, Arg.Any<CancellationToken>()).Returns(item);
        }

        return (repository, queries);
    }

    private static IIntegrationEventPublisher PublisherAcceptingMessages()
    {
        return Substitute.For<IIntegrationEventPublisher>();
    }

    private static bool IsExpectedDecrease(
        IIntegrationEvent message,
        Guid inventoryItemId,
        Guid productId,
        int quantity,
        int currentStock)
    {
        var decreased = message as ProductStockDecreasedIntegrationEvent;
        return decreased?.InventoryItemId == inventoryItemId &&
               decreased.ProductId == productId &&
               decreased.DecreasedQuantity == quantity &&
               decreased.CurrentStock == currentStock;
    }

    private static bool IsExpectedIncrease(
        IIntegrationEvent message,
        Guid productId,
        int quantity,
        int currentStock)
    {
        var increased = message as ProductStockIncreasedIntegrationEvent;
        return increased?.ProductId == productId &&
               increased.DecreasedQuantity == quantity &&
               increased.CurrentStock == currentStock;
    }

    private static bool IsExpectedReturn(
        IIntegrationEvent message,
        Guid productId,
        int quantity,
        int currentStock)
    {
        var returned = message as ProductStockReturnedIntegrationEvent;
        return returned?.ProductId == productId &&
               returned.DecreasedQuantity == quantity &&
               returned.CurrentStock == currentStock;
    }
}
