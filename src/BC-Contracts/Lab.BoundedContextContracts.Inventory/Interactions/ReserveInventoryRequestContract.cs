namespace Lab.BoundedContextContracts.Inventory.Interactions;

/// <summary>
/// 保留庫存的要求資料
/// </summary>
/// <remarks>
/// 跨領域合約
/// </remarks>
public record ReserveInventoryRequestContract : IInventoryRequestContract
{
    public Guid ProductId { get; init; }
    public int Quantity { get; init; }
}