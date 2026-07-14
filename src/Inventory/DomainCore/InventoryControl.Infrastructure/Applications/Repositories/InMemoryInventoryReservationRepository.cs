using InventoryControl.Applications.Reservations;

namespace InventoryControl.Infrastructure.Applications.Repositories;

public sealed class InMemoryInventoryReservationRepository : IInventoryReservationRepository
{
    private readonly object sync = new();
    private readonly Dictionary<Guid, StockItem> inventory = new();
    private readonly Dictionary<Guid, InventoryReservationOutcome> outcomes = new();

    public void Seed(Guid inventoryItemId, Guid productId, int stock)
    {
        lock (sync)
        {
            inventory[productId] = new StockItem(inventoryItemId, stock);
        }
    }

    public int? GetStock(Guid productId)
    {
        lock (sync)
        {
            return inventory.TryGetValue(productId, out var item) ? item.Stock : null;
        }
    }

    public Task<InventoryReservationOutcome> ReserveAsync(
        Guid operationId,
        Guid productId,
        int quantity,
        CancellationToken cancellationToken)
    {
        cancellationToken.ThrowIfCancellationRequested();
        lock (sync)
        {
            if (outcomes.TryGetValue(operationId, out var existing))
            {
                if (existing.ProductId != productId || existing.Quantity != quantity)
                {
                    return Task.FromResult(new InventoryReservationOutcome(
                        operationId, productId, quantity, null, false, null,
                        "OperationIdentityConflict", true));
                }

                return Task.FromResult(existing with { WasAlreadyProcessed = true });
            }

            InventoryReservationOutcome outcome;
            if (!inventory.TryGetValue(productId, out var item))
            {
                outcome = Failed(operationId, productId, quantity, "InventoryItemNotFound");
            }
            else if (item.Stock < quantity)
            {
                outcome = Failed(
                    operationId, productId, quantity, "InventoryIsNotEnough", item.InventoryItemId, item.Stock);
            }
            else
            {
                item.Stock -= quantity;
                outcome = new InventoryReservationOutcome(
                    operationId, productId, quantity, item.InventoryItemId, true, item.Stock, null, false);
            }

            outcomes.Add(operationId, outcome);
            return Task.FromResult(outcome);
        }
    }

    private static InventoryReservationOutcome Failed(
        Guid operationId,
        Guid productId,
        int quantity,
        string reason,
        Guid? inventoryItemId = null,
        int? remainingStock = null)
    {
        return new InventoryReservationOutcome(
            operationId, productId, quantity, inventoryItemId, false, remainingStock, reason, false);
    }

    private sealed class StockItem(Guid inventoryItemId, int stock)
    {
        public Guid InventoryItemId { get; } = inventoryItemId;
        public int Stock { get; set; } = stock;
    }
}
