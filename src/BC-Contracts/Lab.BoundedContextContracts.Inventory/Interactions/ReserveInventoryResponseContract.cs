namespace Lab.BoundedContextContracts.Inventory.Interactions;

/// <summary>
/// 保留庫存的結果回應
/// </summary>
/// <remarks>
/// 跨領域合約
/// </remarks>
public record ReserveInventoryResponseContract
{
    public bool Result { get; set; }
}