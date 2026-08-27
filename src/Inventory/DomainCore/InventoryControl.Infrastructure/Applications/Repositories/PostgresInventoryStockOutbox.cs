using Dapper;
using InventoryControl.Applications.Outbox;
using InventoryControl.Domains;
using Lab.BuildingBlocks.Application;
using Npgsql;

namespace InventoryControl.Infrastructure.Applications.Repositories;

public sealed class PostgresInventoryStockOutbox(
    string connectionString,
    IDomainEventDispatcher dispatcher) : IInventoryStockOutbox
{
    public async Task SaveAndStageAsync(
        InventoryItem inventoryItem,
        int expectedStock,
        InventoryOutboxMessage message,
        CancellationToken cancellationToken)
    {
        var domainEvents = inventoryItem.DomainEvents.ToArray();
        await using var connection = new NpgsqlConnection(connectionString);
        try
        {
            await connection.OpenAsync(cancellationToken);
            await using var transaction = await connection.BeginTransactionAsync(cancellationToken);

            const string updateSql = """
                UPDATE InventoryItems
                SET Stock = @Stock
                WHERE Id = @Id
                  AND Stock = @ExpectedStock;
                """;
            var affected = await connection.ExecuteAsync(new CommandDefinition(
                updateSql,
                new { inventoryItem.Id, inventoryItem.Stock, ExpectedStock = expectedStock },
                transaction,
                cancellationToken: cancellationToken));

            if (affected != 1)
            {
                throw new InventoryStockConcurrencyException(inventoryItem.Id, expectedStock);
            }

            await InventoryOutboxWriter.StageAsync(connection, transaction, message, cancellationToken);
            await transaction.CommitAsync(cancellationToken);
        }
        catch (NpgsqlException exception)
        {
            throw new InventoryOutboxTransientException(
                $"Inventory item {inventoryItem.Id} and its outbox message could not be committed.",
                exception);
        }

        await dispatcher.DispatchAsync(domainEvents, cancellationToken);
        inventoryItem.ClearDomainEvents();
    }
}
