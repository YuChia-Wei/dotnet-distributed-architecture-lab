using System.Data;
using System.Text.Json;
using Dapper;
using InventoryControl.Applications.Reservations;
using Lab.BuildingBlocks.Integrations;
using Npgsql;

namespace InventoryControl.Infrastructure.Applications.Repositories;

public sealed class PostgresInventoryReservationRepository(string connectionString)
    : IInventoryReservationTransactionFactory
{
    private static readonly JsonSerializerOptions SerializerOptions = new()
    {
        PropertyNameCaseInsensitive = true
    };

    public async Task<IInventoryReservationTransaction> BeginAsync(CancellationToken cancellationToken)
    {
        var connection = new NpgsqlConnection(connectionString);
        try
        {
            await connection.OpenAsync(cancellationToken);
            var transaction = await connection.BeginTransactionAsync(
                IsolationLevel.ReadCommitted,
                cancellationToken);
            return new Transaction(connection, transaction);
        }
        catch (NpgsqlException exception)
        {
            await connection.DisposeAsync();
            throw Transient("Inventory reservation transaction could not reach its durable store.", exception);
        }
        catch
        {
            await connection.DisposeAsync();
            throw;
        }
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

    private static InventoryReservationTransientException Transient(string message, NpgsqlException exception)
        => new(message, exception);

    private sealed class Transaction(
        NpgsqlConnection connection,
        NpgsqlTransaction transaction) : IInventoryReservationTransaction
    {
        private bool committed;

        public async Task<InventoryReservationOutcome> ReserveAsync(
            Guid operationId,
            Guid productId,
            int quantity,
            CancellationToken cancellationToken)
        {
            try
            {
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
                    return await ReadExistingAsync(
                        operationId,
                        productId,
                        quantity,
                        cancellationToken);
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
                    outcome = Failed(
                        operationId,
                        productId,
                        quantity,
                        "InventoryIsNotEnough",
                        inventory.Id,
                        inventory.Stock);
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
                        operationId,
                        productId,
                        quantity,
                        inventory.Id,
                        true,
                        remainingStock,
                        null,
                        false);
                }

                await SaveOutcomeAsync(outcome, cancellationToken);
                return outcome;
            }
            catch (NpgsqlException exception)
            {
                throw Transient(
                    $"Inventory reservation {operationId} could not reach its durable store.",
                    exception);
            }
        }

        public async Task StageAsync(
            IIntegrationEvent integrationEvent,
            IntegrationMessageDelivery delivery,
            CancellationToken cancellationToken)
        {
            try
            {
                const string sql = """
                    INSERT INTO InventoryIntegrationOutbox
                        (Id, PartitionKey, MessageType, Data, OccurredOn)
                    VALUES
                        (@Id, @PartitionKey, @MessageType, @Data::jsonb, @OccurredOn)
                    ON CONFLICT (Id) DO NOTHING;
                    """;
                await connection.ExecuteAsync(new CommandDefinition(
                    sql,
                    new
                    {
                        Id = delivery.MessageId,
                        delivery.PartitionKey,
                        MessageType = integrationEvent.GetType().Name,
                        Data = JsonSerializer.Serialize(
                            integrationEvent,
                            integrationEvent.GetType(),
                            SerializerOptions),
                        integrationEvent.OccurredOn
                    },
                    transaction,
                    cancellationToken: cancellationToken));
            }
            catch (NpgsqlException exception)
            {
                throw Transient(
                    $"Inventory outbox message {delivery.MessageId} could not be staged.",
                    exception);
            }
        }

        public async Task CommitAsync(CancellationToken cancellationToken)
        {
            try
            {
                await transaction.CommitAsync(cancellationToken);
                this.committed = true;
            }
            catch (NpgsqlException exception)
            {
                throw Transient("Inventory reservation transaction could not be committed.", exception);
            }
        }

        public async ValueTask DisposeAsync()
        {
            if (!this.committed)
            {
                try
                {
                    await transaction.RollbackAsync(CancellationToken.None);
                }
                catch (NpgsqlException)
                {
                    // Preserve the original application failure; disposal is best effort.
                }
            }

            await transaction.DisposeAsync();
            await connection.DisposeAsync();
        }

        private async Task<InventoryReservationOutcome> ReadExistingAsync(
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
                return Failed(
                    operationId,
                    productId,
                    quantity,
                    "OperationIdentityConflict",
                    wasAlreadyProcessed: true);
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

        private Task SaveOutcomeAsync(
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
                operationId,
                productId,
                quantity,
                inventoryItemId,
                false,
                remainingStock,
                reason,
                wasAlreadyProcessed);
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
}
