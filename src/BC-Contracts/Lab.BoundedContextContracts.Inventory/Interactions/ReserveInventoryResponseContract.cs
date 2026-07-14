namespace Lab.BoundedContextContracts.Inventory.Interactions;

/// <summary>
/// 保留庫存的結果回應
/// </summary>
/// <remarks>
/// 跨領域合約
/// </remarks>
public record ReserveInventoryResponseContract
{
    public Guid OperationId { get; init; }
    public bool Result { get; set; }
    public string? FailureReason { get; init; }
}
