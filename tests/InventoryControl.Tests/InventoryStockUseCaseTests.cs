using InventoryControl.Applications.Repositories;
using InventoryControl.Applications.Queries;
using InventoryControl.Applications.UseCases;
using InventoryControl.Applications.Outbox;
using InventoryControl.Domains;
using Lab.BoundedContextContracts.Inventory.IntegrationEvents;
using NSubstitute;
using Shouldly;

namespace InventoryControl.Tests;

/// <summary>Broker-free GWT coverage for high-risk Inventory mutations.</summary>
public sealed class InventoryStockUseCaseTests
{
    /// <summary>Available stock is persisted and announced after a successful decrease.</summary>
    [Fact]
    public async Task given_sufficient_stock_when_stock_is_decreased_then_state_and_event_are_staged()
    {
        // Given
        var productId = Guid.CreateVersion7();
        var item = new InventoryItem(productId, 10);
        var (repository, queries) = RepositoriesReturning(productId, item);
        var outbox = OutboxAcceptingMessages();
        var useCase = new DecreaseStockUseCase(repository, queries, outbox);

        // When
        var result = await useCase.ExecuteAsync(new DecreaseStockInput(productId, 4), CancellationToken.None);

        // Then
        result.IsSuccess.ShouldBeTrue();
        result.Value.ShouldNotBeNull();
        result.Value.CurrentStock.ShouldBe(6);
        item.Stock.ShouldBe(6);
        await outbox.Received(1).SaveAndStageAsync(
            item,
            10,
            Arg.Is<InventoryOutboxMessage>(message => IsExpectedDecrease(message, item.Id, productId, 4, 6)),
            Arg.Any<CancellationToken>());
    }

    /// <summary>Insufficient stock is a business failure without persistence or publication.</summary>
    [Fact]
    public async Task given_insufficient_stock_when_stock_is_decreased_then_state_and_side_effects_are_unchanged()
    {
        // Given
        var productId = Guid.CreateVersion7();
        var item = new InventoryItem(productId, 2);
        var (repository, queries) = RepositoriesReturning(productId, item);
        var outbox = Substitute.For<IInventoryStockOutbox>();
        var useCase = new DecreaseStockUseCase(repository, queries, outbox);

        // When
        var result = await useCase.ExecuteAsync(new DecreaseStockInput(productId, 3), CancellationToken.None);

        // Then
        result.IsSuccess.ShouldBeFalse();
        result.ErrorMessage.ShouldBe("Available stock is not enough.");
        item.Stock.ShouldBe(2);
        item.DomainEvents.ShouldBeEmpty();
        await outbox.DidNotReceiveWithAnyArgs().SaveAndStageAsync(default!, default, default!, default);
    }

    /// <summary>A missing item suppresses persistence and the stock-decreased success message.</summary>
    [Fact]
    public async Task given_inventory_item_is_missing_when_stock_is_decreased_then_failure_has_no_side_effects()
    {
        // Given
        var productId = Guid.CreateVersion7();
        var (repository, queries) = RepositoriesReturning(productId, null);
        var outbox = Substitute.For<IInventoryStockOutbox>();
        var useCase = new DecreaseStockUseCase(repository, queries, outbox);

        // When
        var result = await useCase.ExecuteAsync(new DecreaseStockInput(productId, 1), CancellationToken.None);

        // Then
        result.IsSuccess.ShouldBeFalse();
        result.ErrorMessage.ShouldBe("InventoryItemNotFound");
        await outbox.DidNotReceiveWithAnyArgs().SaveAndStageAsync(default!, default, default!, default);
    }

    /// <summary>Increasing stock persists the aggregate and publishes the resulting current stock.</summary>
    [Fact]
    public async Task given_inventory_item_exists_when_stock_is_increased_then_state_and_event_are_staged()
    {
        // Given
        var productId = Guid.CreateVersion7();
        var item = new InventoryItem(productId, 5);
        var (repository, queries) = RepositoriesReturning(productId, item);
        var outbox = OutboxAcceptingMessages();
        var useCase = new IncreaseStockUseCase(repository, queries, outbox);

        // When
        var result = await useCase.ExecuteAsync(new IncreaseStockInput(productId, 4), CancellationToken.None);

        // Then
        result.IsSuccess.ShouldBeTrue();
        result.Value!.CurrentStock.ShouldBe(9);
        await outbox.Received(1).SaveAndStageAsync(
            item,
            5,
            Arg.Is<InventoryOutboxMessage>(message => IsExpectedIncrease(message, productId, 4, 9)),
            Arg.Any<CancellationToken>());
    }

    /// <summary>Restocking persists the aggregate and publishes the returned quantity.</summary>
    [Fact]
    public async Task given_inventory_item_exists_when_stock_is_restocked_then_state_and_event_are_staged()
    {
        // Given
        var productId = Guid.CreateVersion7();
        var item = new InventoryItem(productId, 5);
        var (repository, queries) = RepositoriesReturning(productId, item);
        var outbox = OutboxAcceptingMessages();
        var useCase = new RestockUseCase(repository, queries, outbox);

        // When
        var result = await useCase.ExecuteAsync(new RestockInput(productId, 2), CancellationToken.None);

        // Then
        result.IsSuccess.ShouldBeTrue();
        result.Value!.CurrentStock.ShouldBe(7);
        await outbox.Received(1).SaveAndStageAsync(
            item,
            5,
            Arg.Is<InventoryOutboxMessage>(message => IsExpectedReturn(message, productId, 2, 7)),
            Arg.Any<CancellationToken>());
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

    private static IInventoryStockOutbox OutboxAcceptingMessages()
    {
        return Substitute.For<IInventoryStockOutbox>();
    }

    private static bool IsExpectedDecrease(
        InventoryOutboxMessage message,
        Guid inventoryItemId,
        Guid productId,
        int quantity,
        int currentStock)
    {
        var decreased = message.IntegrationEvent as ProductStockDecreasedIntegrationEvent;
        return decreased?.InventoryItemId == inventoryItemId &&
               decreased.ProductId == productId &&
               decreased.DecreasedQuantity == quantity &&
               decreased.CurrentStock == currentStock &&
               message.Delivery.MessageId != Guid.Empty &&
               message.Delivery.PartitionKey == productId.ToString("N");
    }

    private static bool IsExpectedIncrease(
        InventoryOutboxMessage message,
        Guid productId,
        int quantity,
        int currentStock)
    {
        var increased = message.IntegrationEvent as ProductStockIncreasedIntegrationEvent;
        return increased?.ProductId == productId &&
               increased.IncreasedQuantity == quantity &&
               increased.CurrentStock == currentStock &&
               message.Delivery.MessageId != Guid.Empty &&
               message.Delivery.PartitionKey == productId.ToString("N");
    }

    private static bool IsExpectedReturn(
        InventoryOutboxMessage message,
        Guid productId,
        int quantity,
        int currentStock)
    {
        var returned = message.IntegrationEvent as ProductStockReturnedIntegrationEvent;
        return returned?.ProductId == productId &&
               returned.ReturnedQuantity == quantity &&
               returned.CurrentStock == currentStock &&
               message.Delivery.MessageId != Guid.Empty &&
               message.Delivery.PartitionKey == productId.ToString("N");
    }
}
