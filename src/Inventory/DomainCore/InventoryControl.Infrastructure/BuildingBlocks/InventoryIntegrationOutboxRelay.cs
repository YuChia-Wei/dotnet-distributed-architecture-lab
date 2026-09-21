using System.Text.Json;
using InventoryControl.Infrastructure.Applications.Repositories;
using InventoryControl.Infrastructure.Persistence;
using Lab.BoundedContextContracts.Inventory.IntegrationEvents;
using Lab.BuildingBlocks.Integrations;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

namespace InventoryControl.Infrastructure.BuildingBlocks;

internal sealed class InventoryIntegrationOutboxRelay(
    IServiceScopeFactory scopeFactory,
    InventoryOutboxRelayOptions options,
    ILogger<InventoryIntegrationOutboxRelay> logger) : BackgroundService
{
    private const int BatchSize = 20;
    private const int MaxAttempts = 5;
    private const int MaxErrorLength = 4000;
    private const int LeaseSeconds = 30;

    private static readonly IReadOnlyDictionary<string, Type> MessageTypes =
        new Dictionary<string, Type>(StringComparer.Ordinal)
        {
            [nameof(ProductStockDecreasedIntegrationEvent)] = typeof(ProductStockDecreasedIntegrationEvent),
            [nameof(ProductStockIncreasedIntegrationEvent)] = typeof(ProductStockIncreasedIntegrationEvent),
            [nameof(ProductStockReturnedIntegrationEvent)] = typeof(ProductStockReturnedIntegrationEvent)
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

    internal async Task RelayBatchAsync(CancellationToken cancellationToken)
    {
        await using var scope = scopeFactory.CreateAsyncScope();
        var context = scope.ServiceProvider.GetRequiredService<InventoryDbContext>();
        var publisher = scope.ServiceProvider.GetRequiredService<IIntegrationEventPublisher>();
        var lockId = Guid.CreateVersion7();

        await context.Database.ExecuteSqlAsync($"""
            WITH claimed AS (
                SELECT id FROM inventoryintegrationoutbox
                WHERE publishedat IS NULL AND parkedat IS NULL AND nextattemptat <= NOW()
                  AND (lockeduntil IS NULL OR lockeduntil < NOW())
                ORDER BY nextattemptat, createdon, id
                FOR UPDATE SKIP LOCKED
                LIMIT {BatchSize}
            )
            UPDATE inventoryintegrationoutbox AS target
            SET lockid = {lockId}, lockeduntil = NOW() + ({LeaseSeconds} * INTERVAL '1 second'),
                attempts = attempts + 1
            FROM claimed WHERE target.id = claimed.id;
            """, cancellationToken);

        var rows = await context.OutboxMessages.AsNoTracking()
            .Where(row => row.LockId == lockId)
            .OrderBy(row => row.NextAttemptAt).ThenBy(row => row.CreatedOn).ThenBy(row => row.Id)
            .ToListAsync(cancellationToken);
        foreach (var row in rows)
        {
            cancellationToken.ThrowIfCancellationRequested();
            try
            {
                await publisher.PublishAsync(Deserialize(row), new IntegrationMessageDelivery(row.Id, row.PartitionKey));
                await context.OutboxMessages.Where(message => message.Id == row.Id && message.LockId == lockId)
                    .ExecuteUpdateAsync(setters => setters
                        .SetProperty(message => message.PublishedAt, message => DateTime.UtcNow)
                        .SetProperty(message => message.LockId, (Guid?)null)
                        .SetProperty(message => message.LockedUntil, (DateTime?)null)
                        .SetProperty(message => message.LastError, (string?)null), cancellationToken);
            }
            catch (OperationCanceledException) when (cancellationToken.IsCancellationRequested)
            {
                throw;
            }
            catch (Exception exception)
            {
                await this.RecordFailureAsync(context, row, lockId, exception, cancellationToken);
            }
        }

        if (options.RetentionMode == InventoryOutboxRetentionMode.PublishedForDays)
        {
            var days = options.PublishedRetentionDays!.Value;
            await context.OutboxMessages
                .Where(message => message.PublishedAt != null && message.PublishedAt < DateTime.UtcNow.AddDays(-days))
                .ExecuteDeleteAsync(cancellationToken);
        }
    }

    private async Task RecordFailureAsync(InventoryDbContext context, InventoryOutboxRecord row, Guid lockId,
        Exception exception, CancellationToken cancellationToken)
    {
        var isParked = row.Attempts >= MaxAttempts;
        var delaySeconds = Math.Min(60, 1 << Math.Min(row.Attempts, 6));
        var error = exception.ToString();
        if (error.Length > MaxErrorLength)
        {
            error = error[..MaxErrorLength];
        }

        await context.OutboxMessages.Where(message => message.Id == row.Id && message.LockId == lockId)
            .ExecuteUpdateAsync(setters => setters
                .SetProperty(message => message.LockId, (Guid?)null)
                .SetProperty(message => message.LockedUntil, (DateTime?)null)
                .SetProperty(message => message.LastError, error)
                .SetProperty(message => message.NextAttemptAt, message => isParked ? message.NextAttemptAt : DateTime.UtcNow.AddSeconds(delaySeconds))
                .SetProperty(message => message.ParkedAt, message => isParked ? DateTime.UtcNow : (DateTime?)null), cancellationToken);

        if (isParked)
        {
            logger.LogError(exception, "Parked Inventory outbox message {MessageId} after {Attempts} attempts.", row.Id, row.Attempts);
        }
        else
        {
            logger.LogWarning(exception,
                "Inventory outbox message {MessageId} failed attempt {Attempts}; retrying in {DelaySeconds} seconds.",
                row.Id, row.Attempts, delaySeconds);
        }
    }

    private static IIntegrationEvent Deserialize(InventoryOutboxRecord row)
    {
        if (!MessageTypes.TryGetValue(row.MessageType, out var messageType))
        {
            throw new InvalidOperationException($"Unsupported Inventory outbox message type '{row.MessageType}'.");
        }

        return (IIntegrationEvent)(JsonSerializer.Deserialize(row.Data, messageType, InventoryOutboxWriter.SerializerOptions)
            ?? throw new JsonException($"Could not deserialize Inventory outbox row {row.Id}."));
    }
}
