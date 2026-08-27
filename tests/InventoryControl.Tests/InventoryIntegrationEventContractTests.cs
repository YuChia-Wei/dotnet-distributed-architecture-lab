using System.Text.Json;
using Lab.BoundedContextContracts.Inventory.IntegrationEvents;
using Shouldly;

namespace InventoryControl.Tests;

public sealed class InventoryIntegrationEventContractTests
{
    [Fact]
    public void given_an_increase_event_when_serialized_then_the_quantity_name_matches_its_business_meaning()
    {
        var message = new ProductStockIncreasedIntegrationEvent(
            Guid.CreateVersion7(),
            Guid.CreateVersion7(),
            4,
            9);

        var json = JsonSerializer.Serialize(message);

        json.ShouldContain("\"IncreasedQuantity\":4");
        json.ShouldNotContain("DecreasedQuantity");
    }

    [Fact]
    public void given_a_return_event_when_serialized_then_the_quantity_name_matches_its_business_meaning()
    {
        var message = new ProductStockReturnedIntegrationEvent(
            Guid.CreateVersion7(),
            Guid.CreateVersion7(),
            2,
            7);

        var json = JsonSerializer.Serialize(message);

        json.ShouldContain("\"ReturnedQuantity\":2");
        json.ShouldNotContain("DecreasedQuantity");
    }

    [Fact]
    public void given_a_staged_decrease_event_when_deserialized_then_the_original_occurrence_time_is_preserved()
    {
        var occurredOn = new DateTime(2026, 8, 27, 0, 0, 0, DateTimeKind.Utc);
        var message = new ProductStockDecreasedIntegrationEvent(
            Guid.CreateVersion7(),
            Guid.CreateVersion7(),
            2,
            3,
            occurredOn);

        var replayed = JsonSerializer.Deserialize<ProductStockDecreasedIntegrationEvent>(
            JsonSerializer.Serialize(message));

        replayed.ShouldNotBeNull();
        replayed.OccurredOn.ShouldBe(occurredOn);
        replayed.DecreasedQuantity.ShouldBe(2);
    }
}
