using Microsoft.Extensions.Configuration;

namespace Lab.BuildingBlocks.Integrations.Configuration;

/// <summary>Supported messaging transport profiles for a composition root.</summary>
public enum MessagingTransportProfile
{
    InMemory,
    Kafka,
    RabbitMq
}

/// <summary>Provides one validated configuration contract for broker selection.</summary>
public sealed class MessagingTransportOptions
{
    public const string SectionName = "Messaging";

    public MessagingTransportProfile Profile { get; private init; }

    public string? KafkaConnectionString { get; private init; }

    public string? RabbitMqConnectionString { get; private init; }

    public static MessagingTransportOptions FromConfiguration(IConfiguration configuration)
    {
        var section = configuration.GetRequiredSection(SectionName);
        var profileValue = section[nameof(Profile)];
        if (!Enum.TryParse<MessagingTransportProfile>(profileValue, true, out var profile)
            || !Enum.IsDefined(profile))
        {
            throw new InvalidOperationException(
                $"{SectionName}:{nameof(Profile)} must be one of: InMemory, Kafka, RabbitMq.");
        }

        var options = new MessagingTransportOptions
        {
            Profile = profile,
            KafkaConnectionString = section["Kafka:ConnectionString"],
            RabbitMqConnectionString = section["RabbitMq:ConnectionString"]
        };

        options.Validate();
        return options;
    }

    public string GetRequiredKafkaConnectionString()
        => this.KafkaConnectionString!;

    public Uri GetRequiredRabbitMqUri()
        => new(this.RabbitMqConnectionString!, UriKind.Absolute);

    private void Validate()
    {
        if (this.Profile == MessagingTransportProfile.Kafka
            && string.IsNullOrWhiteSpace(this.KafkaConnectionString))
        {
            throw new InvalidOperationException(
                $"{SectionName}:Kafka:ConnectionString is required for the Kafka profile.");
        }

        if (this.Profile != MessagingTransportProfile.RabbitMq)
        {
            return;
        }

        if (!Uri.TryCreate(this.RabbitMqConnectionString, UriKind.Absolute, out var uri)
            || (uri.Scheme != "amqp" && uri.Scheme != "amqps"))
        {
            throw new InvalidOperationException(
                $"{SectionName}:RabbitMq:ConnectionString must be an absolute amqp or amqps URI for the RabbitMq profile.");
        }
    }
}
