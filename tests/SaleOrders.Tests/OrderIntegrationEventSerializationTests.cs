using System.Text.Json;
using System.Text.Json.Nodes;
using Lab.BoundedContextContracts.Orders.IntegrationEvents;
using Lab.BuildingBlocks.Integrations;
using Shouldly;

namespace SaleOrders.Tests;

/// <summary>驗證 Orders 整合事件重建時保留原始發生時間及訊息欄位。</summary>
public sealed class OrderIntegrationEventSerializationTests
{
    private static readonly JsonSerializerOptions SerializerOptions = new()
    {
        PropertyNameCaseInsensitive = true
    };

    /// <summary>對應 source-outbox 測試規格情境 3：儲存後重建不得改變事件內容。</summary>
    [Theory]
    [InlineData(typeof(OrderPlaced))]
    [InlineData(typeof(OrderCancelled))]
    [InlineData(typeof(OrderShipped))]
    [InlineData(typeof(OrderDelivered))]
    public void Should_preserve_stored_payload_when_order_event_is_round_tripped(Type eventType)
    {
        var occurredOn = new DateTime(2000, 1, 1, 0, 0, 0, DateTimeKind.Utc).AddTicks(1234567);
        var storedJson = GivenStoredOrderEvent(eventType, Guid.NewGuid(), Guid.NewGuid(), occurredOn);

        var (restored, reloaded, serializedJson) = WhenRoundTrippingStoredEvent(storedJson, eventType);

        ThenOccurrenceTimeIsPreserved(restored, occurredOn);
        ThenOccurrenceTimeIsPreserved(reloaded, occurredOn);
        ThenAllStoredFieldsArePreserved(storedJson, serializedJson);
    }

    /// <summary>既有 producer 建構式仍以建立當下的 UTC 時間初始化事件。</summary>
    [Theory]
    [InlineData(typeof(OrderPlaced))]
    [InlineData(typeof(OrderCancelled))]
    [InlineData(typeof(OrderShipped))]
    [InlineData(typeof(OrderDelivered))]
    public void Should_record_current_utc_when_producer_creates_order_event(Type eventType)
    {
        var (orderId, productId, beforeCreation) = GivenNewOrderEventIdentifiers();

        var (created, afterCreation) = WhenCreatingProducerEvent(eventType, orderId, productId);

        ThenOccurrenceTimeIsCurrentUtc(created, beforeCreation, afterCreation);
    }

    private static string GivenStoredOrderEvent(Type eventType, Guid orderId, Guid productId, DateTime occurredOn)
        => eventType == typeof(OrderPlaced)
            ? JsonSerializer.Serialize(new { OrderId = orderId, ProductId = productId, ProductName = "test product", Quantity = 3, OccurredOn = occurredOn })
            : JsonSerializer.Serialize(new { OrderId = orderId, Reason = "customer request", OccurredOn = occurredOn });

    private static (IIntegrationEvent Restored, IIntegrationEvent Reloaded, string SerializedJson)
        WhenRoundTrippingStoredEvent(string storedJson, Type eventType)
    {
        var restored = (IIntegrationEvent)JsonSerializer.Deserialize(storedJson, eventType, SerializerOptions)!;
        var serializedJson = JsonSerializer.Serialize(restored, eventType, SerializerOptions);
        var reloaded = (IIntegrationEvent)JsonSerializer.Deserialize(serializedJson, eventType, SerializerOptions)!;
        return (restored, reloaded, serializedJson);
    }

    private static void ThenOccurrenceTimeIsPreserved(IIntegrationEvent actual, DateTime expected)
    {
        actual.ShouldNotBeNull();
        actual.OccurredOn.ShouldBe(expected);
        actual.OccurredOn.Kind.ShouldBe(DateTimeKind.Utc);
    }

    private static void ThenAllStoredFieldsArePreserved(string storedJson, string serializedJson)
        => JsonNode.DeepEquals(JsonNode.Parse(storedJson), JsonNode.Parse(serializedJson)).ShouldBeTrue();

    private static (Guid OrderId, Guid ProductId, DateTime BeforeCreation) GivenNewOrderEventIdentifiers()
        => (Guid.NewGuid(), Guid.NewGuid(), DateTime.UtcNow);

    private static (IIntegrationEvent Created, DateTime AfterCreation) WhenCreatingProducerEvent(
        Type eventType, Guid orderId, Guid productId)
    {
        IIntegrationEvent created = eventType.Name switch
        {
            nameof(OrderPlaced) => new OrderPlaced(orderId, productId, "test product", 3),
            nameof(OrderCancelled) => new OrderCancelled(orderId, "customer request"),
            nameof(OrderShipped) => new OrderShipped(orderId, "customer request"),
            nameof(OrderDelivered) => new OrderDelivered(orderId, "customer request"),
            _ => throw new ArgumentOutOfRangeException(nameof(eventType))
        };
        return (created, DateTime.UtcNow);
    }

    private static void ThenOccurrenceTimeIsCurrentUtc(IIntegrationEvent actual, DateTime before, DateTime after)
    {
        actual.OccurredOn.Kind.ShouldBe(DateTimeKind.Utc);
        actual.OccurredOn.ShouldBeInRange(before, after);
    }
}
