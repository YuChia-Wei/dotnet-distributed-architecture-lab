namespace InventoryControl.Infrastructure.Persistence;

internal sealed class InventoryGoodsReceiptRecord
{
    public Guid ReceiptId { get; set; }
    public Guid PurchaseOrderId { get; set; }
    public Guid ProductId { get; set; }
    public int Quantity { get; set; }
    public Guid? InventoryItemId { get; set; }
    public int? ResultingStock { get; set; }
    public DateTime? CompletedAt { get; set; }
}
