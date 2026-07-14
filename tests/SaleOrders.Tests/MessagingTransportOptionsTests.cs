using Lab.BuildingBlocks.Integrations.Configuration;
using Microsoft.Extensions.Configuration;
using Shouldly;

namespace SaleOrders.Tests;

public sealed class MessagingTransportOptionsTests
{
    [Fact]
    public void Given_in_memory_profile_when_configuration_is_parsed_then_no_broker_connection_is_required()
    {
        var configuration = CreateConfiguration(("Messaging:Profile", "InMemory"));

        var options = MessagingTransportOptions.FromConfiguration(configuration);

        options.Profile.ShouldBe(MessagingTransportProfile.InMemory);
    }

    [Fact]
    public void Given_kafka_profile_without_connection_when_configuration_is_parsed_then_startup_validation_fails()
    {
        var configuration = CreateConfiguration(("Messaging:Profile", "Kafka"));

        var exception = Should.Throw<InvalidOperationException>(
            () => MessagingTransportOptions.FromConfiguration(configuration));

        exception.Message.ShouldContain("Messaging:Kafka:ConnectionString");
    }

    [Fact]
    public void Given_rabbitmq_profile_with_invalid_uri_when_configuration_is_parsed_then_startup_validation_fails()
    {
        var configuration = CreateConfiguration(
            ("Messaging:Profile", "RabbitMq"),
            ("Messaging:RabbitMq:ConnectionString", "http://localhost"));

        var exception = Should.Throw<InvalidOperationException>(
            () => MessagingTransportOptions.FromConfiguration(configuration));

        exception.Message.ShouldContain("amqp or amqps");
    }

    [Fact]
    public void Given_unknown_profile_when_configuration_is_parsed_then_startup_validation_fails()
    {
        var configuration = CreateConfiguration(("Messaging:Profile", "Unknown"));

        var exception = Should.Throw<InvalidOperationException>(
            () => MessagingTransportOptions.FromConfiguration(configuration));

        exception.Message.ShouldContain("InMemory, Kafka, RabbitMq");
    }

    private static IConfiguration CreateConfiguration(params (string Key, string Value)[] values)
    {
        var entries = values.ToDictionary(pair => pair.Key, pair => (string?)pair.Value);
        return new ConfigurationBuilder()
            .AddInMemoryCollection(entries)
            .Build();
    }
}
