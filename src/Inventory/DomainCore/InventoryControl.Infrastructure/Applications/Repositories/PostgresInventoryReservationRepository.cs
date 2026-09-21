using System.Data;
using InventoryControl.Applications.Outbox;
using InventoryControl.Applications.Reservations;
using InventoryControl.Infrastructure.Persistence;
using Microsoft.EntityFrameworkCore;
using Npgsql;

namespace InventoryControl.Infrastructure.Applications.Repositories;

public sealed class PostgresInventoryReservationRepository(InventoryDbContext context) : IInventoryReservationOutbox
{
    public async Task<InventoryReservationOutcome> ReserveAndStageAsync(
        Guid operationId,
        Guid productId,
        int quantity,
        Func<InventoryReservationOutcome, InventoryOutboxMessage> successfulMessageFactory,
        CancellationToken cancellationToken)
    {
        try
        {
            await using var transaction = await context.Database.BeginTransactionAsync(IsolationLevel.ReadCommitted, cancellationToken);
            var claimed = await context.Database.ExecuteSqlAsync($"""
                INSERT INTO inventoryreservationoperations (operationid, productid, quantity, completedat)
                VALUES ({operationId}, {productId}, {quantity}, NULL)
                ON CONFLICT (operationid) DO NOTHING;
                """, cancellationToken);

            var outcome = claimed == 0
                ? await this.ReadExistingAsync(operationId, productId, quantity, cancellationToken)
                : await this.ReserveAsync(operationId, productId, quantity, cancellationToken);

            if (outcome.IsSuccess && !outcome.WasAlreadyProcessed)
            {
                var message = successfulMessageFactory(outcome)
                    ?? throw new InvalidOperationException("A successful reservation requires an outbox message.");
                await InventoryOutboxWriter.StageAsync(context, message, cancellationToken);
            }

            await context.SaveChangesAsync(cancellationToken);
            await transaction.CommitAsync(cancellationToken);
            context.ChangeTracker.Clear();
            return outcome;
        }
        catch (Exception exception) when (exception is NpgsqlException || exception is DbUpdateException { InnerException: NpgsqlException })
        {
            context.ChangeTracker.Clear();
            throw new InventoryReservationTransientException(
                $"Inventory reservation {operationId} could not reach its durable store.", exception);
        }
        catch
        {
            context.ChangeTracker.Clear();
            throw;
        }
    }

    private async Task<InventoryReservationOutcome> ReserveAsync(Guid operationId, Guid productId, int quantity, CancellationToken cancellationToken)
    {
        var rows = await context.InventoryItems.FromSql($"""
            SELECT id, productid, stock FROM inventoryitems WHERE productid = {productId} FOR UPDATE
            """).AsNoTracking().ToListAsync(cancellationToken);
        var inventory = rows.SingleOrDefault();
        InventoryReservationOutcome outcome;
        if (inventory is null)
        {
            outcome = Failed(operationId, productId, quantity, "InventoryItemNotFound");
        }
        else if (inventory.Stock < quantity)
        {
            outcome = Failed(operationId, productId, quantity, "InventoryIsNotEnough", inventory.Id, inventory.Stock);
        }
        else
        {
            context.DetachInventoryItem(inventory.Id);
            var remainingStock = inventory.Stock - quantity;
            await context.InventoryItems.Where(item => item.Id == inventory.Id)
                .ExecuteUpdateAsync(setters => setters.SetProperty(item => item.Stock, remainingStock), cancellationToken);
            outcome = new InventoryReservationOutcome(operationId, productId, quantity, inventory.Id, true, remainingStock, null, false);
        }

        var operation = await context.ReservationOperations.SingleAsync(row => row.OperationId == operationId, cancellationToken);
        operation.InventoryItemId = outcome.InventoryItemId;
        operation.IsSuccess = outcome.IsSuccess;
        operation.RemainingStock = outcome.RemainingStock;
        operation.FailureReason = outcome.FailureReason;
        operation.CompletedAt = DateTime.UtcNow;
        return outcome;
    }

    private async Task<InventoryReservationOutcome> ReadExistingAsync(Guid operationId, Guid productId, int quantity, CancellationToken cancellationToken)
    {
        var row = await context.ReservationOperations.AsNoTracking()
            .SingleAsync(operation => operation.OperationId == operationId, cancellationToken);
        if (row.ProductId != productId || row.Quantity != quantity)
        {
            return Failed(operationId, productId, quantity, "OperationIdentityConflict", wasAlreadyProcessed: true);
        }

        return new InventoryReservationOutcome(row.OperationId, row.ProductId, row.Quantity, row.InventoryItemId,
            row.IsSuccess == true, row.RemainingStock, row.FailureReason, true);
    }

    private static InventoryReservationOutcome Failed(Guid operationId, Guid productId, int quantity, string reason,
        Guid? inventoryItemId = null, int? remainingStock = null, bool wasAlreadyProcessed = false)
        => new(operationId, productId, quantity, inventoryItemId, false, remainingStock, reason, wasAlreadyProcessed);
}
