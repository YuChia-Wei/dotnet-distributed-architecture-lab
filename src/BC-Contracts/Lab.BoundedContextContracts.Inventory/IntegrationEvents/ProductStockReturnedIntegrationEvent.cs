using System.Text.Json.Serialization;
using Lab.BuildingBlocks.Integrations;

namespace Lab.BoundedContextContracts.Inventory.IntegrationEvents;

public class ProductStockReturnedIntegrationEvent : IIntegrationEvent
{
    public ProductStockReturnedIntegrationEvent(
        Guid inventoryItemId,
        Guid productId,
        int returnedQuantity,
        int currentStock)
        : this(inventoryItemId, productId, returnedQuantity, currentStock, DateTime.UtcNow)
    {
    }

    [JsonConstructor]
    public ProductStockReturnedIntegrationEvent(
        Guid inventoryItemId,
        Guid productId,
        int returnedQuantity,
        int currentStock,
        DateTime occurredOn)
    {
        this.InventoryItemId = inventoryItemId;
        this.ProductId = productId;
        this.ReturnedQuantity = returnedQuantity;
        this.CurrentStock = currentStock;
        this.OccurredOn = occurredOn;
    }

    public Guid InventoryItemId { get; }
    public Guid ProductId { get; }
    public int ReturnedQuantity { get; }
    public int CurrentStock { get; }

    /// <summary>
    /// 發生時間
    /// </summary>
    public DateTime OccurredOn { get; }
}
