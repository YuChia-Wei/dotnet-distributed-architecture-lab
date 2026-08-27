using InventoryControl.Applications.Reservations;
using Lab.BuildingBlocks.Integrations;

namespace InventoryControl.Infrastructure.Applications.Repositories;

public sealed class InMemoryInventoryReservationRepository : IInventoryReservationTransactionFactory
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

    public async Task<IInventoryReservationTransaction> BeginAsync(CancellationToken cancellationToken)
    {
        await this.transactionGate.WaitAsync(cancellationToken);
        return new Transaction(this);
    }

    public async Task<InventoryReservationOutcome> ReserveAsync(
        Guid operationId,
        Guid productId,
        int quantity,
        CancellationToken cancellationToken)
    {
        await using var transaction = await this.BeginAsync(cancellationToken);
        var outcome = await transaction.ReserveAsync(operationId, productId, quantity, cancellationToken);
        await transaction.CommitAsync(cancellationToken);
        return outcome;
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

    private void StageCore(IIntegrationEvent integrationEvent, IntegrationMessageDelivery delivery)
    {
        if (this.outbox.TryGetValue(delivery.MessageId, out var existing))
        {
            if (existing.IntegrationEvent.GetType() != integrationEvent.GetType() ||
                existing.Delivery.PartitionKey != delivery.PartitionKey)
            {
                throw new InvalidOperationException(
                    $"Outbox message identity {delivery.MessageId} is already bound to another payload.");
            }

            return;
        }

        this.outbox.Add(delivery.MessageId, new StagedIntegrationMessage(integrationEvent, delivery));
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

    public sealed record StagedIntegrationMessage(
        IIntegrationEvent IntegrationEvent,
        IntegrationMessageDelivery Delivery);

    private sealed class Transaction : IInventoryReservationTransaction
    {
        private readonly InMemoryInventoryReservationRepository owner;
        private readonly Dictionary<Guid, StockItem> inventorySnapshot;
        private readonly Dictionary<Guid, InventoryReservationOutcome> outcomesSnapshot;
        private readonly Dictionary<Guid, StagedIntegrationMessage> outboxSnapshot;
        private bool committed;
        private bool disposed;

        public Transaction(InMemoryInventoryReservationRepository owner)
        {
            this.owner = owner;
            this.inventorySnapshot = owner.inventory.ToDictionary(
                pair => pair.Key,
                pair => new StockItem(pair.Value.InventoryItemId, pair.Value.Stock));
            this.outcomesSnapshot = new Dictionary<Guid, InventoryReservationOutcome>(owner.outcomes);
            this.outboxSnapshot = new Dictionary<Guid, StagedIntegrationMessage>(owner.outbox);
        }

        public Task<InventoryReservationOutcome> ReserveAsync(
            Guid operationId,
            Guid productId,
            int quantity,
            CancellationToken cancellationToken)
        {
            cancellationToken.ThrowIfCancellationRequested();
            return Task.FromResult(this.owner.ReserveCore(operationId, productId, quantity));
        }

        public Task StageAsync(
            IIntegrationEvent integrationEvent,
            IntegrationMessageDelivery delivery,
            CancellationToken cancellationToken)
        {
            cancellationToken.ThrowIfCancellationRequested();
            this.owner.StageCore(integrationEvent, delivery);
            return Task.CompletedTask;
        }

        public Task CommitAsync(CancellationToken cancellationToken)
        {
            cancellationToken.ThrowIfCancellationRequested();
            this.committed = true;
            return Task.CompletedTask;
        }

        public ValueTask DisposeAsync()
        {
            if (this.disposed)
            {
                return ValueTask.CompletedTask;
            }

            if (!this.committed)
            {
                Restore(this.owner.inventory, this.inventorySnapshot);
                Restore(this.owner.outcomes, this.outcomesSnapshot);
                Restore(this.owner.outbox, this.outboxSnapshot);
            }

            this.disposed = true;
            this.owner.transactionGate.Release();
            return ValueTask.CompletedTask;
        }

        private static void Restore<T>(Dictionary<Guid, T> target, Dictionary<Guid, T> snapshot)
        {
            target.Clear();
            foreach (var pair in snapshot)
            {
                target.Add(pair.Key, pair.Value);
            }
        }
    }

    private sealed class StockItem(Guid inventoryItemId, int stock)
    {
        public Guid InventoryItemId { get; } = inventoryItemId;
        public int Stock { get; set; } = stock;
    }
}
