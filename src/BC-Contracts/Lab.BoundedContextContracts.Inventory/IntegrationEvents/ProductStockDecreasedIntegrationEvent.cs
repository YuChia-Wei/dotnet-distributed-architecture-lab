using Lab.BuildingBlocks.Integrations;

namespace Lab.BoundedContextContracts.Inventory.IntegrationEvents;

public class ProductStockDecreasedIntegrationEvent : IIntegrationEvent
{
    public ProductStockDecreasedIntegrationEvent(Guid inventoryItemId, Guid productId, int decreasedQuantity, int currentStock)
    {
        this.InventoryItemId = inventoryItemId;
        this.ProductId = productId;
        this.DecreasedQuantity = decreasedQuantity;
        this.CurrentStock = currentStock;
        this.OccurredOn = DateTime.UtcNow;
    }

    public Guid InventoryItemId { get; }
    public Guid ProductId { get; }
    public int DecreasedQuantity { get; }
    public int CurrentStock { get; }

    /// <summary>
    /// 發生時間
    /// </summary>
    public DateTime OccurredOn { get; }
}