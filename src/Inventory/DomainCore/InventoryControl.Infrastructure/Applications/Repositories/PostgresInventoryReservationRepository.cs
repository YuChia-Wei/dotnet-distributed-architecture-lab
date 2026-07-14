using System.Data;
using Dapper;
using InventoryControl.Applications.Reservations;
using Npgsql;

namespace InventoryControl.Infrastructure.Applications.Repositories;

public sealed class PostgresInventoryReservationRepository(string connectionString)
    : IInventoryReservationRepository
{
    public async Task<InventoryReservationOutcome> ReserveAsync(
        Guid operationId,
        Guid productId,
        int quantity,
        CancellationToken cancellationToken)
    {
        try
        {
            await using var connection = new NpgsqlConnection(connectionString);
            await connection.OpenAsync(cancellationToken);
            await using var transaction = await connection.BeginTransactionAsync(
                IsolationLevel.ReadCommitted,
                cancellationToken);

            const string claimSql = """
                INSERT INTO InventoryReservationOperations
                    (OperationId, ProductId, Quantity, CompletedAt)
                VALUES
                    (@OperationId, @ProductId, @Quantity, NULL)
                ON CONFLICT (OperationId) DO NOTHING
                RETURNING OperationId;
                """;

            var claimed = await connection.QuerySingleOrDefaultAsync<Guid?>(new CommandDefinition(
                claimSql,
                new { OperationId = operationId, ProductId = productId, Quantity = quantity },
                transaction,
                cancellationToken: cancellationToken));

            if (claimed is null)
            {
                var replay = await ReadExistingAsync(
                    connection,
                    transaction,
                    operationId,
                    productId,
                    quantity,
                    cancellationToken);
                await transaction.CommitAsync(cancellationToken);
                return replay;
            }

            const string inventorySql = """
                SELECT Id, Stock
                FROM InventoryItems
                WHERE ProductId = @ProductId
                FOR UPDATE;
                """;
            var inventory = await connection.QuerySingleOrDefaultAsync<InventoryRow>(new CommandDefinition(
                inventorySql,
                new { ProductId = productId },
                transaction,
                cancellationToken: cancellationToken));

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
                const string decreaseSql = """
                    UPDATE InventoryItems
                    SET Stock = Stock - @Quantity
                    WHERE Id = @InventoryItemId
                    RETURNING Stock;
                    """;
                var remainingStock = await connection.QuerySingleAsync<int>(new CommandDefinition(
                    decreaseSql,
                    new { Quantity = quantity, InventoryItemId = inventory.Id },
                    transaction,
                    cancellationToken: cancellationToken));
                outcome = new InventoryReservationOutcome(
                    operationId, productId, quantity, inventory.Id, true, remainingStock, null, false);
            }

            await SaveOutcomeAsync(connection, transaction, outcome, cancellationToken);
            await transaction.CommitAsync(cancellationToken);
            return outcome;
        }
        catch (NpgsqlException exception)
        {
            throw new InventoryReservationTransientException(
                $"Inventory reservation {operationId} could not reach its durable store.",
                exception);
        }
    }

    private static async Task<InventoryReservationOutcome> ReadExistingAsync(
        NpgsqlConnection connection,
        NpgsqlTransaction transaction,
        Guid operationId,
        Guid productId,
        int quantity,
        CancellationToken cancellationToken)
    {
        const string sql = """
            SELECT OperationId, ProductId, Quantity, InventoryItemId, IsSuccess,
                   RemainingStock, FailureReason
            FROM InventoryReservationOperations
            WHERE OperationId = @OperationId;
            """;
        var row = await connection.QuerySingleAsync<ReservationRow>(new CommandDefinition(
            sql,
            new { OperationId = operationId },
            transaction,
            cancellationToken: cancellationToken));

        if (row.ProductId != productId || row.Quantity != quantity)
        {
            return Failed(operationId, productId, quantity, "OperationIdentityConflict", wasAlreadyProcessed: true);
        }

        return new InventoryReservationOutcome(
            row.OperationId,
            row.ProductId,
            row.Quantity,
            row.InventoryItemId,
            row.IsSuccess,
            row.RemainingStock,
            row.FailureReason,
            true);
    }

    private static Task SaveOutcomeAsync(
        NpgsqlConnection connection,
        NpgsqlTransaction transaction,
        InventoryReservationOutcome outcome,
        CancellationToken cancellationToken)
    {
        const string sql = """
            UPDATE InventoryReservationOperations
            SET InventoryItemId = @InventoryItemId,
                IsSuccess = @IsSuccess,
                RemainingStock = @RemainingStock,
                FailureReason = @FailureReason,
                CompletedAt = CURRENT_TIMESTAMP
            WHERE OperationId = @OperationId;
            """;
        return connection.ExecuteAsync(new CommandDefinition(
            sql,
            outcome,
            transaction,
            cancellationToken: cancellationToken));
    }

    private static InventoryReservationOutcome Failed(
        Guid operationId,
        Guid productId,
        int quantity,
        string reason,
        Guid? inventoryItemId = null,
        int? remainingStock = null,
        bool wasAlreadyProcessed = false)
    {
        return new InventoryReservationOutcome(
            operationId, productId, quantity, inventoryItemId, false, remainingStock, reason, wasAlreadyProcessed);
    }

    private sealed record InventoryRow(Guid Id, int Stock);

    private sealed record ReservationRow(
        Guid OperationId,
        Guid ProductId,
        int Quantity,
        Guid? InventoryItemId,
        bool IsSuccess,
        int? RemainingStock,
        string? FailureReason);
}
