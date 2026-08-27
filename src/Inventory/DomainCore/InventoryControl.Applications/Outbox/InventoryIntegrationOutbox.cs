using InventoryControl.Domains;
using Lab.BuildingBlocks.Integrations;

namespace InventoryControl.Applications.Outbox;

/// <summary>
/// A producer-owned integration event and the stable transport metadata that must be persisted with it.
/// </summary>
public sealed record InventoryOutboxMessage(
    IIntegrationEvent IntegrationEvent,
    IntegrationMessageDelivery Delivery);

/// <summary>
/// Atomically persists one Inventory aggregate mutation and its outgoing integration event.
/// </summary>
/// <remarks>
/// This is intentionally narrower than a generic Unit of Work. The Infrastructure adapter may use a
/// local database transaction internally, but Application code depends on the business capability it needs.
/// </remarks>
public interface IInventoryStockOutbox
{
    Task SaveAndStageAsync(
        InventoryItem inventoryItem,
        int expectedStock,
        InventoryOutboxMessage message,
        CancellationToken cancellationToken);
}

public sealed class InventoryStockConcurrencyException(Guid inventoryItemId, int expectedStock)
    : Exception(
        $"Inventory item {inventoryItemId} no longer has the expected stock value {expectedStock}.")
{
}

public sealed class InventoryOutboxTransientException : Exception
{
    public InventoryOutboxTransientException(string message, Exception innerException)
        : base(message, innerException)
    {
    }
}
