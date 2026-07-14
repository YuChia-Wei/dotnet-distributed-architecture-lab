using System.Data;
using System.Text.Json;
using Dapper;
using Lab.BoundedContextContracts.Orders.IntegrationEvents;
using Lab.BuildingBlocks.Integrations;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

namespace SaleOrders.Infrastructure.BuildingBlocks;

/// <summary>Relays atomically committed Orders outbox rows through Wolverine.</summary>
internal sealed class OrderIntegrationOutboxRelay(
    IServiceScopeFactory scopeFactory,
    ILogger<OrderIntegrationOutboxRelay> logger) : BackgroundService
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
            [nameof(OrderPlaced)] = typeof(OrderPlaced),
            [nameof(OrderCancelled)] = typeof(OrderCancelled),
            [nameof(OrderShipped)] = typeof(OrderShipped),
            [nameof(OrderDelivered)] = typeof(OrderDelivered)
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
                logger.LogError(exception, "Failed to relay the Orders integration outbox batch.");
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

        const string claimSql = @"
        WITH claimed AS (
            SELECT Id
            FROM OrderIntegrationOutbox
            WHERE ParkedAt IS NULL
              AND NextAttemptAt <= NOW()
              AND (LockedUntil IS NULL OR LockedUntil < NOW())
            ORDER BY NextAttemptAt, CreatedOn, Id
            FOR UPDATE SKIP LOCKED
            LIMIT @BatchSize
        )
        UPDATE OrderIntegrationOutbox AS target
        SET LockId = @LockId,
            LockedUntil = NOW() + (@LeaseSeconds * INTERVAL '1 second'),
            Attempts = Attempts + 1
        FROM claimed
        WHERE target.Id = claimed.Id
        RETURNING target.Id,
                  target.AggregateId,
                  target.MessageType,
                  target.Data::text AS Data,
                  target.Attempts";

        var rows = await connection.QueryAsync<OutboxRow>(
            new CommandDefinition(
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
                    new IntegrationMessageDelivery(row.Id, row.AggregateId.ToString("D")));

                await connection.ExecuteAsync(
                    new CommandDefinition(
                        "DELETE FROM OrderIntegrationOutbox WHERE Id = @Id AND LockId = @LockId",
                        new
                        {
                            row.Id,
                            LockId = lockId
                        },
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

        const string failureSql = @"
        UPDATE OrderIntegrationOutbox
        SET LockId = NULL,
            LockedUntil = NULL,
            LastError = @LastError,
            NextAttemptAt = CASE
                WHEN @IsParked THEN NextAttemptAt
                ELSE NOW() + (@DelaySeconds * INTERVAL '1 second')
            END,
            ParkedAt = CASE WHEN @IsParked THEN NOW() ELSE NULL END
        WHERE Id = @Id
          AND LockId = @LockId";

        await connection.ExecuteAsync(
            new CommandDefinition(
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
                "Parked Orders outbox message {MessageId} after {Attempts} attempts.",
                row.Id,
                row.Attempts);
        }
        else
        {
            logger.LogWarning(
                exception,
                "Orders outbox message {MessageId} failed attempt {Attempts}; retrying in {DelaySeconds} seconds.",
                row.Id,
                row.Attempts,
                delaySeconds);
        }
    }

    private static IIntegrationEvent Deserialize(OutboxRow row)
    {
        if (!MessageTypes.TryGetValue(row.MessageType, out var messageType))
        {
            throw new InvalidOperationException($"Unsupported Orders outbox message type '{row.MessageType}'.");
        }

        return (IIntegrationEvent)(JsonSerializer.Deserialize(row.Data, messageType, SerializerOptions)
            ?? throw new JsonException($"Could not deserialize Orders outbox row {row.Id}."));
    }

    private sealed record OutboxRow(
        Guid Id,
        Guid AggregateId,
        string MessageType,
        string Data,
        int Attempts);
}
