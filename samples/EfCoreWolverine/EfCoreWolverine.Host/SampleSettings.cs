using Microsoft.Extensions.Configuration;

namespace EfCoreWolverine.Host;

public sealed record SampleSettings(string ConnectionString, string KafkaBootstrapServers,
    string RequestTopic, string EventTopic, string ConsumerGroup, string MessageSchema)
{
    public static SampleSettings FromConfiguration(IConfiguration configuration)
        => new(Required(configuration, "ConnectionStrings:Sample"),
            Required(configuration, "Kafka:BootstrapServers"),
            configuration["Kafka:RequestTopic"] ?? "ef-inventory-sample.requests",
            configuration["Kafka:EventTopic"] ?? "ef-inventory-sample.events",
            configuration["Kafka:ConsumerGroup"] ?? "ef-inventory-sample",
            configuration["MessageSchema"] ?? "ef_inventory_messages");

    private static string Required(IConfiguration configuration, string key)
        => !string.IsNullOrWhiteSpace(configuration[key]) ? configuration[key]!
            : throw new InvalidOperationException($"Configure {key} before running this sample.");
}
