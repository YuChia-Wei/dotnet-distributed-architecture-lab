using System.Text.Json.Serialization;
using Lab.BuildingBlocks.Integrations;

namespace Lab.BoundedContextContracts.Inventory.IntegrationEvents;

public class ProductStockIncreasedIntegrationEvent : IIntegrationEvent
{
    public ProductStockIncreasedIntegrationEvent(
        Guid inventoryItemId,
        Guid productId,
        int increasedQuantity,
        int currentStock)
        : this(inventoryItemId, productId, increasedQuantity, currentStock, DateTime.UtcNow)
    {
    }

    [JsonConstructor]
    public ProductStockIncreasedIntegrationEvent(
        Guid inventoryItemId,
        Guid productId,
        int increasedQuantity,
        int currentStock,
        DateTime occurredOn)
    {
        this.InventoryItemId = inventoryItemId;
        this.ProductId = productId;
        this.IncreasedQuantity = increasedQuantity;
        this.CurrentStock = currentStock;
        this.OccurredOn = occurredOn;
    }

    public Guid InventoryItemId { get; }
    public Guid ProductId { get; }
    public int IncreasedQuantity { get; }
    public int CurrentStock { get; }

    /// <summary>
    /// 發生時間
    /// </summary>
    public DateTime OccurredOn { get; }
}
