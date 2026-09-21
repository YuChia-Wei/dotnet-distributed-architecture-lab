using System.Text.Json;
using InventoryControl.Applications.Outbox;
using InventoryControl.Infrastructure.Persistence;
using Microsoft.EntityFrameworkCore;

namespace InventoryControl.Infrastructure.Applications.Repositories;

internal static class InventoryOutboxWriter
{
    internal static readonly JsonSerializerOptions SerializerOptions = new() { PropertyNameCaseInsensitive = true };

    /// <summary>Stages a stable message identity in the caller-owned transaction, including successful replays.</summary>
    public static Task StageAsync(InventoryDbContext context, InventoryOutboxMessage message, CancellationToken cancellationToken)
    {
        var messageType = message.IntegrationEvent.GetType().Name;
        var data = JsonSerializer.Serialize(message.IntegrationEvent, message.IntegrationEvent.GetType(), SerializerOptions);
        return context.Database.ExecuteSqlAsync($"""
            INSERT INTO inventoryintegrationoutbox (id, partitionkey, messagetype, data, occurredon)
            VALUES ({message.Delivery.MessageId}, {message.Delivery.PartitionKey}, {messageType}, {data}::jsonb, {message.IntegrationEvent.OccurredOn})
            ON CONFLICT (id) DO NOTHING;
            """, cancellationToken);
    }
}
