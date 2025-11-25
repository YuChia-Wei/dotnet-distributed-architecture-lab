using System;
using Lab.BuildingBlocks.Domains;

namespace InventoryControl.Domains.DomainEvents;

public class StockDecreased : IDomainEvent
{
    public StockDecreased(Guid inventoryItemId, Guid productId, int decreasedQuantity, int currentStock)
    {
        this.InventoryItemId = inventoryItemId;
        this.ProductId = productId;
        this.DecreasedQuantity = decreasedQuantity;
        this.CurrentStock = currentStock;
        this.OccurredOn = DateTime.UtcNow;
    }

    public Guid ProductId { get; set; }

    public Guid InventoryItemId { get; }
    public int DecreasedQuantity { get; }
    public int CurrentStock { get; }

    /// <summary>
    /// 事件發生的時間
    /// </summary>
    public DateTime OccurredOn { get; }
}