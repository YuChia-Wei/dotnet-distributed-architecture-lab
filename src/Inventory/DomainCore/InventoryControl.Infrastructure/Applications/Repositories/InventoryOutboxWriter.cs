using System.Text.Json;
using Dapper;
using InventoryControl.Applications.Outbox;
using Npgsql;

namespace InventoryControl.Infrastructure.Applications.Repositories;

internal static class InventoryOutboxWriter
{
    private static readonly JsonSerializerOptions SerializerOptions = new()
    {
        PropertyNameCaseInsensitive = true
    };

    public static Task StageAsync(
        NpgsqlConnection connection,
        NpgsqlTransaction transaction,
        InventoryOutboxMessage message,
        CancellationToken cancellationToken)
    {
        const string sql = """
            INSERT INTO InventoryIntegrationOutbox
                (Id, PartitionKey, MessageType, Data, OccurredOn)
            VALUES
                (@Id, @PartitionKey, @MessageType, @Data::jsonb, @OccurredOn)
            ON CONFLICT (Id) DO NOTHING;
            """;

        return connection.ExecuteAsync(new CommandDefinition(
            sql,
            new
            {
                Id = message.Delivery.MessageId,
                message.Delivery.PartitionKey,
                MessageType = message.IntegrationEvent.GetType().Name,
                Data = JsonSerializer.Serialize(
                    message.IntegrationEvent,
                    message.IntegrationEvent.GetType(),
                    SerializerOptions),
                message.IntegrationEvent.OccurredOn
            },
            transaction,
            cancellationToken: cancellationToken));
    }
}
