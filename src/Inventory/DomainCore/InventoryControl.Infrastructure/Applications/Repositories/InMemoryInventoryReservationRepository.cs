using InventoryControl.Applications.Outbox;
using InventoryControl.Applications.Reservations;

namespace InventoryControl.Infrastructure.Applications.Repositories;

public sealed class InMemoryInventoryReservationRepository : IInventoryReservationOutbox
{
    private readonly SemaphoreSlim transactionGate = new(1, 1);
    private readonly Dictionary<Guid, StockItem> inventory = new();
    private readonly Dictionary<Guid, InventoryReservationOutcome> outcomes = new();
    private readonly Dictionary<Guid, StagedIntegrationMessage> outbox = new();

    public void Seed(Guid inventoryItemId, Guid productId, int stock)
    {
        this.inventory[productId] = new StockItem(inventoryItemId, stock);
    }

    public int? GetStock(Guid productId)
        => this.inventory.TryGetValue(productId, out var item) ? item.Stock : null;

    public IReadOnlyList<StagedIntegrationMessage> GetStagedMessages()
        => this.outbox.Values.ToArray();

    public async Task<InventoryReservationOutcome> ReserveAndStageAsync(
        Guid operationId,
        Guid productId,
        int quantity,
        Func<InventoryReservationOutcome, InventoryOutboxMessage> successfulMessageFactory,
        CancellationToken cancellationToken)
    {
        await this.transactionGate.WaitAsync(cancellationToken);
        var inventorySnapshot = this.inventory.ToDictionary(
            pair => pair.Key,
            pair => new StockItem(pair.Value.InventoryItemId, pair.Value.Stock));
        var outcomesSnapshot = new Dictionary<Guid, InventoryReservationOutcome>(this.outcomes);
        var outboxSnapshot = new Dictionary<Guid, StagedIntegrationMessage>(this.outbox);

        try
        {
            var outcome = this.ReserveCore(operationId, productId, quantity);
            if (outcome.IsSuccess)
            {
                var message = successfulMessageFactory(outcome)
                    ?? throw new InvalidOperationException("A successful reservation requires an outbox message.");
                this.StageCore(message);
            }

            return outcome;
        }
        catch
        {
            Restore(this.inventory, inventorySnapshot);
            Restore(this.outcomes, outcomesSnapshot);
            Restore(this.outbox, outboxSnapshot);
            throw;
        }
        finally
        {
            this.transactionGate.Release();
        }
    }

    private InventoryReservationOutcome ReserveCore(Guid operationId, Guid productId, int quantity)
    {
        if (this.outcomes.TryGetValue(operationId, out var existing))
        {
            if (existing.ProductId != productId || existing.Quantity != quantity)
            {
                return new InventoryReservationOutcome(
                    operationId, productId, quantity, null, false, null,
                    "OperationIdentityConflict", true);
            }

            return existing with { WasAlreadyProcessed = true };
        }

        InventoryReservationOutcome outcome;
        if (!this.inventory.TryGetValue(productId, out var item))
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

        this.outcomes.Add(operationId, outcome);
        return outcome;
    }

    private void StageCore(InventoryOutboxMessage message)
    {
        if (this.outbox.TryGetValue(message.Delivery.MessageId, out var existing))
        {
            if (existing.IntegrationEvent.GetType() != message.IntegrationEvent.GetType() ||
                existing.Delivery.PartitionKey != message.Delivery.PartitionKey)
            {
                throw new InvalidOperationException(
                    $"Outbox message identity {message.Delivery.MessageId} is already bound to another payload.");
            }

            return;
        }

        this.outbox.Add(
            message.Delivery.MessageId,
            new StagedIntegrationMessage(message.IntegrationEvent, message.Delivery));
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

    private static void Restore<T>(Dictionary<Guid, T> target, Dictionary<Guid, T> snapshot)
    {
        target.Clear();
        foreach (var pair in snapshot)
        {
            target.Add(pair.Key, pair.Value);
        }
    }

    public sealed record StagedIntegrationMessage(
        Lab.BuildingBlocks.Integrations.IIntegrationEvent IntegrationEvent,
        Lab.BuildingBlocks.Integrations.IntegrationMessageDelivery Delivery);

    private sealed class StockItem(Guid inventoryItemId, int stock)
    {
        public Guid InventoryItemId { get; } = inventoryItemId;
        public int Stock { get; set; } = stock;
    }
}
