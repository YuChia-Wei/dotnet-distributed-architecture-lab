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

        if (connection.State != ConnectionState.Open)
        {
            connection.Open();
        }

        const string claimSql = @"
        WITH claimed AS (
            SELECT Id
            FROM OrderIntegrationOutbox
            WHERE LockedUntil IS NULL OR LockedUntil < NOW()
            ORDER BY CreatedOn
            FOR UPDATE SKIP LOCKED
            LIMIT 20
        )
        UPDATE OrderIntegrationOutbox AS target
        SET LockedUntil = NOW() + INTERVAL '30 seconds', Attempts = Attempts + 1
        FROM claimed
        WHERE target.Id = claimed.Id
        RETURNING target.Id, target.AggregateId, target.MessageType, target.Data::text AS Data";

        var rows = await connection.QueryAsync<OutboxRow>(claimSql);
        foreach (var row in rows)
        {
            cancellationToken.ThrowIfCancellationRequested();
            var message = Deserialize(row);
            await publisher.PublishAsync(
                message,
                new IntegrationMessageDelivery(row.Id, row.AggregateId.ToString("D")));

            await connection.ExecuteAsync(
                "DELETE FROM OrderIntegrationOutbox WHERE Id = @Id",
                new { row.Id });
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

    private sealed record OutboxRow(Guid Id, Guid AggregateId, string MessageType, string Data);
}
