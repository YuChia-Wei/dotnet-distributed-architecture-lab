using System.Text.Json;
using EfCoreWolverine.Host;
using Lab.BoundedContextContracts.Inventory.IntegrationEvents;
using Microsoft.EntityFrameworkCore;
using Shouldly;

namespace EfCoreWolverine.Tests;

[Trait("Category", "ExternalIntegration")]
public sealed class MessagingTransactionTests(MessagingFixture fixture) : IClassFixture<MessagingFixture>
{
    [ExternalMessagingFact]
    public async Task Given_stock_when_a_real_Kafka_request_completes_then_state_inbox_and_outgoing_event_succeed()
    {
        var item = await fixture.SeedAsync(10);
        var envelopeId = Guid.NewGuid();
        using var events = fixture.EventConsumer();

        await fixture.SendAsync(new DecreaseStockRequested(item.Id, 2), envelopeId);

        await EventuallyAsync(async () => await fixture.InboxStatusAsync(envelopeId) == "Handled");
        (await fixture.StockAsync(item.Id)).ShouldBe(8);
        fixture.Probe.Calls[item.Id].ShouldBe(1);
        using var timeout = CancellationTokenSource.CreateLinkedTokenSource(TestContext.Current.CancellationToken);
        timeout.CancelAfter(TimeSpan.FromSeconds(20));
        ProductStockDecreasedIntegrationEvent? delivered;
        do
        {
            delivered = JsonSerializer.Deserialize<ProductStockDecreasedIntegrationEvent>(events.Consume(timeout.Token).Message.Value,
                new JsonSerializerOptions { PropertyNameCaseInsensitive = true });
        } while (delivered?.InventoryItemId != item.Id);
        delivered.CurrentStock.ShouldBe(8);
        delivered.DecreasedQuantity.ShouldBe(2);
    }

    [ExternalMessagingFact]
    public async Task Given_a_failure_after_SQL_flush_when_processing_ends_then_business_and_outbox_are_rolled_back()
    {
        var item = await fixture.SeedAsync(10);
        var envelopeId = Guid.NewGuid();
        fixture.Probe.RejectAfterFlush[item.Id] = true;
        using var events = fixture.EventConsumer();

        await fixture.SendAsync(new DecreaseStockRequested(item.Id, 2), envelopeId);

        await fixture.Probe.For(item.Id).Task.WaitAsync(TimeSpan.FromSeconds(20), TestContext.Current.CancellationToken);
        await EventuallyAsync(async () => await fixture.InboxStatusAsync(envelopeId) is null or "Error");
        (await fixture.StockAsync(item.Id)).ShouldBe(10);
        (await fixture.OutboxCountAsync()).ShouldBe(0);
        var canary = await fixture.SeedAsync(4);
        await fixture.SendAsync(new DecreaseStockRequested(canary.Id, 1), Guid.NewGuid());
        using var timeout = CancellationTokenSource.CreateLinkedTokenSource(TestContext.Current.CancellationToken);
        timeout.CancelAfter(TimeSpan.FromSeconds(20));
        ProductStockDecreasedIntegrationEvent? observed;
        do
        {
            observed = JsonSerializer.Deserialize<ProductStockDecreasedIntegrationEvent>(
                events.Consume(timeout.Token).Message.Value,
                new JsonSerializerOptions { PropertyNameCaseInsensitive = true });
            observed!.InventoryItemId.ShouldNotBe(item.Id, "A rolled-back operation must not escape to Kafka.");
        } while (observed.InventoryItemId != canary.Id);
        var observeUntil = DateTime.UtcNow.AddSeconds(3);
        while (DateTime.UtcNow < observeUntil)
        {
            TestContext.Current.CancellationToken.ThrowIfCancellationRequested();
            var record = events.Consume(TimeSpan.FromMilliseconds(100));
            if (record is null) continue;
            var escaped = JsonSerializer.Deserialize<ProductStockDecreasedIntegrationEvent>(record.Message.Value,
                new JsonSerializerOptions { PropertyNameCaseInsensitive = true });
            escaped!.InventoryItemId.ShouldNotBe(item.Id, "A rolled-back operation must not escape to Kafka.");
        }
        fixture.Probe.RejectAfterFlush.TryRemove(item.Id, out _);
    }

    [ExternalMessagingFact]
    public async Task Given_duplicate_Kafka_deliveries_when_the_same_envelope_is_replayed_then_stock_changes_only_once()
    {
        var item = await fixture.SeedAsync(10);
        var envelopeId = Guid.NewGuid();
        var request = new DecreaseStockRequested(item.Id, 2);

        await Task.WhenAll(fixture.SendAsync(request, envelopeId), fixture.SendAsync(request, envelopeId));
        await EventuallyAsync(async () => await fixture.InboxStatusAsync(envelopeId) == "Handled");
        await fixture.SendAsync(request, envelopeId);
        var barrierId = Guid.NewGuid();
        await fixture.SendAsync(new DecreaseStockRequested(item.Id, 1), barrierId);
        await EventuallyAsync(async () => await fixture.InboxStatusAsync(barrierId) == "Handled");

        (await fixture.StockAsync(item.Id)).ShouldBe(7);
        fixture.Probe.Calls[item.Id].ShouldBe(2);
    }

    [ExternalMessagingFact]
    public async Task Given_two_repository_contexts_when_both_modify_one_version_then_the_stale_write_fails()
    {
        var item = await fixture.SeedAsync(10);
        await using var first = fixture.NewDb();
        await using var second = fixture.NewDb();
        var firstItem = await first.InventoryItems.SingleAsync(x => x.Id == item.Id, TestContext.Current.CancellationToken);
        var secondItem = await second.InventoryItems.SingleAsync(x => x.Id == item.Id, TestContext.Current.CancellationToken);
        firstItem.DecreaseStock(2);
        secondItem.DecreaseStock(3);

        await first.SaveChangesAsync(TestContext.Current.CancellationToken);

        await Should.ThrowAsync<DbUpdateConcurrencyException>(() => second.SaveChangesAsync(TestContext.Current.CancellationToken));
        (await fixture.StockAsync(item.Id)).ShouldBe(8);
    }

    private static async Task EventuallyAsync(Func<Task<bool>> condition)
    {
        using var timeout = CancellationTokenSource.CreateLinkedTokenSource(TestContext.Current.CancellationToken);
        timeout.CancelAfter(TimeSpan.FromSeconds(25));
        while (!await condition()) await Task.Delay(50, timeout.Token);
    }
}
