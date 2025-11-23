using System;
using Lab.BuildingBlocks.Domains;

namespace InventoryControl.Domains.DomainEvents;

public class StockIncreased : IDomainEvent
{
    public StockIncreased(Guid inventoryItemId, Guid productId, int increasedQuantity, int currentStock)
    {
        this.InventoryItemId = inventoryItemId;
        this.ProductId = productId;
        this.IncreasedQuantity = increasedQuantity;
        this.CurrentStock = currentStock;
        this.OccurredOn = DateTime.UtcNow;
    }

    public Guid InventoryItemId { get; set; }

    public Guid ProductId { get; }
    public int IncreasedQuantity { get; }
    public int CurrentStock { get; }

    /// <summary>
    /// 事件發生的時間
    /// </summary>
    public DateTime OccurredOn { get; }
}