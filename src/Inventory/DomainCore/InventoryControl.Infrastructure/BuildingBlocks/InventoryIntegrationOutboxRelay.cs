using System.Data;
using System.Text.Json;
using Dapper;
using Lab.BoundedContextContracts.Inventory.IntegrationEvents;
using Lab.BuildingBlocks.Integrations;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

namespace InventoryControl.Infrastructure.BuildingBlocks;

internal sealed class InventoryIntegrationOutboxRelay(
    IServiceScopeFactory scopeFactory,
    ILogger<InventoryIntegrationOutboxRelay> logger) : BackgroundService
{
    private const int BatchSize = 20;
    private const int MaxAttempts = 5;
    private const int MaxErrorLength = 4000;
    private const int LeaseSeconds = 30;

    private static readonly JsonSerializerOptions SerializerOptions = new()
    {
        PropertyNameCaseInsensitive = true
    };

    private static readonly IReadOnlyDictionary<string, Type> MessageTypes =
        new Dictionary<string, Type>(StringComparer.Ordinal)
        {
            [nameof(ProductStockDecreasedIntegrationEvent)] = typeof(ProductStockDecreasedIntegrationEvent)
        };

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                await this.RelayBatchAsync(stoppingToken);
            }
            catch (OperationCanceledException) when (stoppingToken.IsCancellationRequested)
            {
                break;
            }
            catch (Exception exception)
            {
                logger.LogError(exception, "Failed to relay the Inventory integration outbox batch.");
            }

            await Task.Delay(TimeSpan.FromSeconds(1), stoppingToken);
        }
    }

    private async Task RelayBatchAsync(CancellationToken cancellationToken)
    {
        using var scope = scopeFactory.CreateScope();
        var connection = scope.ServiceProvider.GetRequiredService<IDbConnection>();
        var publisher = scope.ServiceProvider.GetRequiredService<IIntegrationEventPublisher>();
        var lockId = Guid.CreateVersion7();

        if (connection.State != ConnectionState.Open)
        {
            connection.Open();
        }

        const string claimSql = """
            WITH claimed AS (
                SELECT Id
                FROM InventoryIntegrationOutbox
                WHERE PublishedAt IS NULL
                  AND ParkedAt IS NULL
                  AND NextAttemptAt <= NOW()
                  AND (LockedUntil IS NULL OR LockedUntil < NOW())
                ORDER BY NextAttemptAt, CreatedOn, Id
                FOR UPDATE SKIP LOCKED
                LIMIT @BatchSize
            )
            UPDATE InventoryIntegrationOutbox AS target
            SET LockId = @LockId,
                LockedUntil = NOW() + (@LeaseSeconds * INTERVAL '1 second'),
                Attempts = Attempts + 1
            FROM claimed
            WHERE target.Id = claimed.Id
            RETURNING target.Id,
                      target.PartitionKey,
                      target.MessageType,
                      target.Data::text AS Data,
                      target.Attempts;
            """;

        var rows = await connection.QueryAsync<OutboxRow>(new CommandDefinition(
            claimSql,
            new
            {
                BatchSize,
                LockId = lockId,
                LeaseSeconds
            },
            cancellationToken: cancellationToken));

        foreach (var row in rows)
        {
            cancellationToken.ThrowIfCancellationRequested();
            try
            {
                var message = Deserialize(row);
                await publisher.PublishAsync(
                    message,
                    new IntegrationMessageDelivery(row.Id, row.PartitionKey));

                const string publishedSql = """
                    UPDATE InventoryIntegrationOutbox
                    SET PublishedAt = NOW(),
                        LockId = NULL,
                        LockedUntil = NULL,
                        LastError = NULL
                    WHERE Id = @Id
                      AND LockId = @LockId;
                    """;
                await connection.ExecuteAsync(new CommandDefinition(
                    publishedSql,
                    new { row.Id, LockId = lockId },
                    cancellationToken: cancellationToken));
            }
            catch (OperationCanceledException) when (cancellationToken.IsCancellationRequested)
            {
                throw;
            }
            catch (Exception exception)
            {
                await RecordFailureAsync(connection, row, lockId, exception, cancellationToken);
            }
        }
    }

    private async Task RecordFailureAsync(
        IDbConnection connection,
        OutboxRow row,
        Guid lockId,
        Exception exception,
        CancellationToken cancellationToken)
    {
        var isParked = row.Attempts >= MaxAttempts;
        var delaySeconds = Math.Min(60, 1 << Math.Min(row.Attempts, 6));
        var error = exception.ToString();
        if (error.Length > MaxErrorLength)
        {
            error = error[..MaxErrorLength];
        }

        const string failureSql = """
            UPDATE InventoryIntegrationOutbox
            SET LockId = NULL,
                LockedUntil = NULL,
                LastError = @LastError,
                NextAttemptAt = CASE
                    WHEN @IsParked THEN NextAttemptAt
                    ELSE NOW() + (@DelaySeconds * INTERVAL '1 second')
                END,
                ParkedAt = CASE WHEN @IsParked THEN NOW() ELSE NULL END
            WHERE Id = @Id
              AND LockId = @LockId;
            """;
        await connection.ExecuteAsync(new CommandDefinition(
            failureSql,
            new
            {
                row.Id,
                LockId = lockId,
                LastError = error,
                IsParked = isParked,
                DelaySeconds = delaySeconds
            },
            cancellationToken: cancellationToken));

        if (isParked)
        {
            logger.LogError(
                exception,
                "Parked Inventory outbox message {MessageId} after {Attempts} attempts.",
                row.Id,
                row.Attempts);
        }
        else
        {
            logger.LogWarning(
                exception,
                "Inventory outbox message {MessageId} failed attempt {Attempts}; retrying in {DelaySeconds} seconds.",
                row.Id,
                row.Attempts,
                delaySeconds);
        }
    }

    private static IIntegrationEvent Deserialize(OutboxRow row)
    {
        if (!MessageTypes.TryGetValue(row.MessageType, out var messageType))
        {
            throw new InvalidOperationException(
                $"Unsupported Inventory outbox message type '{row.MessageType}'.");
        }

        return (IIntegrationEvent)(JsonSerializer.Deserialize(row.Data, messageType, SerializerOptions)
            ?? throw new JsonException($"Could not deserialize Inventory outbox row {row.Id}."));
    }

    private sealed record OutboxRow(
        Guid Id,
        string PartitionKey,
        string MessageType,
        string Data,
        int Attempts);
}
