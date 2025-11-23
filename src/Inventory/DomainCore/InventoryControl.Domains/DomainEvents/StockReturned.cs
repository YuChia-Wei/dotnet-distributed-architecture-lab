using System;
using Lab.BuildingBlocks.Domains;

namespace InventoryControl.Domains.DomainEvents;

public class StockReturned : IDomainEvent
{
    public StockReturned(Guid inventoryItemId, Guid productId, int returnedQuantity, int currentStock)
    {
        this.InventoryItemId = inventoryItemId;
        this.ProductId = productId;
        this.ReturnedQuantity = returnedQuantity;
        this.CurrentStock = currentStock;
        throw new NotImplementedException();
    }

    public Guid InventoryItemId { get; set; }

    public Guid ProductId { get; }
    public int ReturnedQuantity { get; }
    public int CurrentStock { get; }

    /// <summary>
    /// 事件發生的時間
    /// </summary>
    public DateTime OccurredOn { get; }
}