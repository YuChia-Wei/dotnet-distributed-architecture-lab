using InventoryControl.Applications.Outbox;
using InventoryControl.Domains;
using InventoryControl.Infrastructure.Persistence;
using Lab.BuildingBlocks.Application;
using Microsoft.EntityFrameworkCore;
using Npgsql;

namespace InventoryControl.Infrastructure.Applications.Repositories;

public sealed class PostgresInventoryStockOutbox(InventoryDbContext context, IDomainEventDispatcher dispatcher)
    : IInventoryStockOutbox
{
    public async Task SaveAndStageAsync(
        InventoryItem inventoryItem,
        int expectedStock,
        InventoryOutboxMessage message,
        CancellationToken cancellationToken)
    {
        var domainEvents = inventoryItem.DomainEvents.ToArray();
        try
        {
            await using var transaction = await context.Database.BeginTransactionAsync(cancellationToken);
            context.DetachInventoryItem(inventoryItem.Id);
            var affected = await context.InventoryItems
                .Where(item => item.Id == inventoryItem.Id && item.Stock == expectedStock)
                .ExecuteUpdateAsync(setters => setters.SetProperty(item => item.Stock, inventoryItem.Stock), cancellationToken);

            if (affected != 1)
            {
                throw new InventoryStockConcurrencyException(inventoryItem.Id, expectedStock);
            }

            await InventoryOutboxWriter.StageAsync(context, message, cancellationToken);
            await transaction.CommitAsync(cancellationToken);
        }
        catch (NpgsqlException exception)
        {
            context.ChangeTracker.Clear();
            throw new InventoryOutboxTransientException(
                $"Inventory item {inventoryItem.Id} and its outbox message could not be committed.", exception);
        }
        catch
        {
            context.ChangeTracker.Clear();
            throw;
        }

        await dispatcher.DispatchAsync(domainEvents, cancellationToken);
        inventoryItem.ClearDomainEvents();
    }
}
