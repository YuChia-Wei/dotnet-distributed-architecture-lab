using InventoryControl.Domains;
using InventoryControl.Domains.DomainEvents;
using Lab.BoundedContextContracts.Inventory.IntegrationEvents;
using Lab.BuildingBlocks.Application;

namespace EfCoreWolverine.Application;

/// <summary>
/// Coordinates the business operation within a transaction owned by the inbound pipeline.
/// Repository and publisher adapters participate in that transaction without committing it.
/// </summary>
public sealed class DecreaseStockUseCase(
    IAggregateRepository<InventoryItem, Guid> repository,
    IStockEventPublisher publisher) : IDecreaseStockUseCase
{
    public async Task<DecreaseStockOutput> ExecuteAsync(
        DecreaseStockInput input,
        CancellationToken cancellationToken)
    {
        ArgumentNullException.ThrowIfNull(input);
        if (input.InventoryItemId == Guid.Empty)
        {
            throw new ArgumentException("An inventory item ID is required.", nameof(input));
        }

        ArgumentOutOfRangeException.ThrowIfNegativeOrZero(input.Quantity);

        var inventoryItem = await repository.FindByIdAsync(input.InventoryItemId, cancellationToken);
        if (inventoryItem is null)
        {
            return new DecreaseStockOutput(false, null, "InventoryItemNotFound");
        }

        var result = inventoryItem.DecreaseStock(input.Quantity);
        if (!result.IsSuccess)
        {
            return new DecreaseStockOutput(false, inventoryItem.Stock, result.ErrorCode);
        }

        await repository.SaveAsync(inventoryItem, cancellationToken);

        var domainEvent = inventoryItem.DomainEvents.OfType<StockDecreased>().Last();
        await publisher.PublishAsync(
            new ProductStockDecreasedIntegrationEvent(
                domainEvent.InventoryItemId,
                domainEvent.ProductId,
                domainEvent.DecreasedQuantity,
                domainEvent.CurrentStock,
                domainEvent.OccurredOn),
            cancellationToken);

        return new DecreaseStockOutput(true, inventoryItem.Stock, null);
    }
}
