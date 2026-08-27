using System.Text.Json.Serialization;
using Lab.BuildingBlocks.Integrations;

namespace Lab.BoundedContextContracts.Inventory.IntegrationEvents;

public class ProductStockDecreasedIntegrationEvent : IIntegrationEvent
{
    public ProductStockDecreasedIntegrationEvent(
        Guid inventoryItemId,
        Guid productId,
        int decreasedQuantity,
        int currentStock)
        : this(inventoryItemId, productId, decreasedQuantity, currentStock, DateTime.UtcNow)
    {
    }

    [JsonConstructor]
    public ProductStockDecreasedIntegrationEvent(
        Guid inventoryItemId,
        Guid productId,
        int decreasedQuantity,
        int currentStock,
        DateTime occurredOn)
    {
        this.InventoryItemId = inventoryItemId;
        this.ProductId = productId;
        this.DecreasedQuantity = decreasedQuantity;
        this.CurrentStock = currentStock;
        this.OccurredOn = occurredOn;
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
