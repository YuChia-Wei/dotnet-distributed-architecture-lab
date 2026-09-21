namespace InventoryControl.Infrastructure.Persistence;

internal sealed class InventoryOutboxRecord
{
    public Guid Id { get; set; }
    public string PartitionKey { get; set; } = string.Empty;
    public string MessageType { get; set; } = string.Empty;
    public string Data { get; set; } = string.Empty;
    public DateTime OccurredOn { get; set; }
    public DateTime CreatedOn { get; set; }
    public DateTime? PublishedAt { get; set; }
    public Guid? LockId { get; set; }
    public DateTime? LockedUntil { get; set; }
    public int Attempts { get; set; }
    public DateTime NextAttemptAt { get; set; }
    public string? LastError { get; set; }
    public DateTime? ParkedAt { get; set; }
}
