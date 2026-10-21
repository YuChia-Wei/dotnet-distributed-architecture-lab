using ArchPrecept.Contracts.Application.Messaging;
using ArchPrecept.Contracts.Messaging;
using InventoryControl.Infrastructure.BuildingBlocks;
using Microsoft.Extensions.Logging;
using NSubstitute;
using Shouldly;
using Wolverine;

namespace InventoryControl.Tests;

public sealed class IntegrationEventPublisherTests
{
    [Fact]
    public async Task Given_delivery_metadata_when_publishing_then_the_adapter_preserves_identity_and_partition()
    {
        var captured = new List<DeliveryOptions>();
        var publisher = GivenPublisherCapturingMetadata(captured);
        var message = new TestIntegrationEvent(DateTime.UnixEpoch);
        var delivery = new IntegrationMessageDelivery(Guid.Parse("11111111-1111-1111-1111-111111111111"), "product-42");

        await WhenPublishing(publisher, message, delivery);

        ThenMetadataIsPreserved(captured, delivery);
    }

    [Fact]
    public async Task Given_a_failed_transport_when_publishing_then_the_original_failure_is_observable()
    {
        var failure = new InvalidOperationException("transport failed");
        var publisher = GivenFailingPublisher(failure);
        var message = new TestIntegrationEvent(DateTime.UnixEpoch);
        var delivery = new IntegrationMessageDelivery(Guid.Empty, "product-42");

        var exception = await Record.ExceptionAsync(() => WhenPublishing(publisher, message, delivery));

        ThenFailureIsPreserved(exception, failure);
    }

    private static IIntegrationEventPublisher GivenPublisherCapturingMetadata(List<DeliveryOptions> captured)
    {
        var bus = Substitute.For<IMessageBus>();
        bus.PublishAsync(Arg.Any<IIntegrationEvent>(), Arg.Do<DeliveryOptions>(captured.Add))
            .Returns(ValueTask.CompletedTask);
        return new IntegrationEventPublisher(bus, Substitute.For<ILogger<IntegrationEventPublisher>>());
    }

    private static IIntegrationEventPublisher GivenFailingPublisher(Exception failure)
    {
        var bus = Substitute.For<IMessageBus>();
        bus.PublishAsync(Arg.Any<IIntegrationEvent>(), Arg.Any<DeliveryOptions>())
            .Returns(ValueTask.FromException(failure));
        return new IntegrationEventPublisher(bus, Substitute.For<ILogger<IntegrationEventPublisher>>());
    }

    private static Task WhenPublishing(
        IIntegrationEventPublisher publisher, IIntegrationEvent message, IntegrationMessageDelivery delivery)
        => publisher.PublishAsync(message, delivery);

    private static void ThenMetadataIsPreserved(List<DeliveryOptions> captured, IntegrationMessageDelivery delivery)
    {
        captured.Count.ShouldBe(1);
        captured[0].DeduplicationId.ShouldBe(delivery.MessageId.ToString("N"));
        captured[0].PartitionKey.ShouldBe(delivery.PartitionKey);
        captured[0].Headers["lab-message-id"].ShouldBe(delivery.MessageId.ToString("D"));
    }

    private static void ThenFailureIsPreserved(Exception? actual, Exception expected)
        => actual.ShouldBeSameAs(expected);

    private sealed record TestIntegrationEvent(DateTime OccurredOn) : IIntegrationEvent;
}
