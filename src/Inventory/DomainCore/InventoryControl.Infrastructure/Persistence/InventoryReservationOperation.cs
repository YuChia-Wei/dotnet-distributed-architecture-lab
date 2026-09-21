namespace InventoryControl.Infrastructure.Persistence;

internal sealed class InventoryReservationOperation
{
    public Guid OperationId { get; set; }
    public Guid ProductId { get; set; }
    public int Quantity { get; set; }
    public Guid? InventoryItemId { get; set; }
    public bool? IsSuccess { get; set; }
    public int? RemainingStock { get; set; }
    public string? FailureReason { get; set; }
    public DateTime? CompletedAt { get; set; }
}
