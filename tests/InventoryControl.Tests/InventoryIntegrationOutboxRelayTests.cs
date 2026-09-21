using System.Collections.Concurrent;
using System.Text.Json;
using InventoryControl.Applications.Reservations;
using InventoryControl.Domains;
using InventoryControl.Infrastructure.Applications.Repositories;
using InventoryControl.Infrastructure.BuildingBlocks;
using InventoryControl.Infrastructure.Persistence;
using Lab.BoundedContextContracts.Inventory.IntegrationEvents;
using Lab.BuildingBlocks.Integrations;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging.Abstractions;
using NSubstitute;
using Shouldly;
using Wolverine;

namespace InventoryControl.Tests;

/// <summary>AC5: actual EF/PostgreSQL claim, retry, parking, retention and stable delivery metadata.</summary>
public sealed class InventoryIntegrationOutboxRelayTests
{
    [Fact]
    public async Task given_a_stable_delivery_when_published_then_wolverine_metadata_matches_the_outbox_identity()
    {
        var (publisher, capturedOptions) = GivenWolverinePublisher();
        var messageId = Guid.CreateVersion7();
        var partitionKey = Guid.CreateVersion7().ToString("N");
        await WhenPublishingDelivery(publisher, messageId, partitionKey);
        ThenWolverineMetadataShouldMatch(capturedOptions, messageId, partitionKey);
    }

    [ExternalIntegrationFact]
    public async Task given_the_same_claimed_row_when_publish_is_retried_then_delivery_identity_and_event_time_are_stable()
    {
        await using var database = await InventoryPostgresDatabase.CreateAsync();
        var row = await GivenPendingMessage(database);
        var publisher = new RecordingPublisher(failures: 1);
        await using var services = GivenRelayServices(database, publisher);
        await WhenRelayingWithRetry(database, services, row.Id);
        await ThenRetriedDeliveryShouldBeStable(database, publisher, row);
    }

    [ExternalIntegrationFact]
    public async Task given_five_transport_failures_when_relay_runs_again_then_the_row_is_parked_and_not_republished()
    {
        await using var database = await InventoryPostgresDatabase.CreateAsync();
        var row = await GivenPendingMessage(database);
        var publisher = new RecordingPublisher(failures: 5);
        await using var services = GivenRelayServices(database, publisher);
        await WhenRelayingThroughFiveFailures(database, services, row.Id);
        await ThenMessageShouldBeParked(database, publisher, row.Id);
    }

    [ExternalIntegrationFact]
    public async Task given_finite_published_retention_when_relay_runs_then_only_expired_published_rows_are_pruned()
    {
        await using var database = await InventoryPostgresDatabase.CreateAsync();
        var (expiredId, recentId, parkedId) = await GivenRetentionRows(database);
        await using var services = GivenRelayServices(database, new RecordingPublisher());
        await WhenRelaying(services, new InventoryOutboxRelayOptions(false, InventoryOutboxRetentionMode.PublishedForDays, 7));
        await ThenRetentionShouldKeepRecentAndUnpublished(database, expiredId, recentId, parkedId);
    }

    /// <summary>R02：成功發布並依保留期限清理後，預留重播不得重建發布意圖。</summary>
    [ExternalIntegrationFact]
    [Trait("Category", "ExternalIntegration")]
    public async Task given_a_published_reservation_was_purged_when_replayed_then_no_new_publication_is_staged()
    {
        await using var database = await InventoryPostgresDatabase.CreateAsync();
        var reservation = await GivenCompletedReservation(database, initialStock: 5, quantity: 2);
        var publisher = new RecordingPublisher();
        await using var services = GivenRelayServices(database, publisher);
        await GivenReservationWasPublishedAndPurged(database, services, publisher, reservation.Input.OperationId, retentionDays: 7);

        var replay = await WhenReplayingReservationAndRelaying(database, services, reservation.Input);

        await ThenReplayShouldNotStageOrPublish(database, publisher, reservation, replay, expectedStock: 3, expectedPublications: 1);
    }

    /// <summary>R02：已完成操作的訊息資料缺失時，重播不得自行補建訊息。</summary>
    [ExternalIntegrationFact]
    [Trait("Category", "ExternalIntegration")]
    public async Task given_a_completed_reservation_has_no_outbox_row_when_replayed_then_no_recovery_publication_is_staged()
    {
        await using var database = await InventoryPostgresDatabase.CreateAsync();
        var reservation = await GivenCompletedReservation(database, initialStock: 5, quantity: 2);
        await GivenReservationOutboxRowIsMissing(database, reservation.Input.OperationId);
        var publisher = new RecordingPublisher();
        await using var services = GivenRelayServices(database, publisher);

        var replay = await WhenReplayingReservationAndRelaying(database, services, reservation.Input);

        await ThenReplayShouldNotStageOrPublish(database, publisher, reservation, replay, expectedStock: 3, expectedPublications: 0);
    }

    [ExternalIntegrationFact]
    public async Task given_one_pending_row_when_two_relays_claim_concurrently_then_only_one_lease_publishes_it()
    {
        await using var database = await InventoryPostgresDatabase.CreateAsync();
        var row = await GivenPendingMessage(database);
        var publisher = new RecordingPublisher();
        await using var services = GivenRelayServices(database, publisher);
        await WhenTwoRelaysRunConcurrently(services);
        await ThenOneDeliveryShouldBePublished(database, publisher, row.Id);
    }

    [ExternalIntegrationFact]
    public async Task given_a_cancelled_batch_when_relay_runs_then_no_message_is_claimed_or_published()
    {
        await using var database = await InventoryPostgresDatabase.CreateAsync();
        var row = await GivenPendingMessage(database);
        var publisher = new RecordingPublisher();
        await using var services = GivenRelayServices(database, publisher);
        var error = await WhenRelayingWithCancellation(services);
        await ThenCancelledBatchShouldLeaveMessagePending(database, publisher, row.Id, error);
    }

    [ExternalIntegrationFact]
    public async Task given_an_expired_lease_when_relay_recovers_then_original_delivery_identity_is_preserved()
    {
        await using var database = await InventoryPostgresDatabase.CreateAsync();
        var row = await GivenExpiredLease(database);
        var publisher = new RecordingPublisher();
        await using var services = GivenRelayServices(database, publisher);
        await WhenRelaying(services);
        await ThenOneDeliveryShouldBePublished(database, publisher, row.Id);
    }

    private static (IntegrationEventPublisher Publisher, List<DeliveryOptions> Options) GivenWolverinePublisher()
    {
        var options = new List<DeliveryOptions>();
        var bus = Substitute.For<IMessageBus>();
        bus.PublishAsync(Arg.Any<IIntegrationEvent>(), Arg.Do<DeliveryOptions>(value => options.Add(value))).Returns(ValueTask.CompletedTask);
        return (new IntegrationEventPublisher(bus, NullLogger<IntegrationEventPublisher>.Instance), options);
    }

    private static Task WhenPublishingDelivery(IntegrationEventPublisher publisher, Guid messageId, string partitionKey)
        => publisher.PublishAsync(new ProductStockDecreasedIntegrationEvent(Guid.CreateVersion7(), Guid.CreateVersion7(), 2, 3),
            new IntegrationMessageDelivery(messageId, partitionKey));

    private static void ThenWolverineMetadataShouldMatch(List<DeliveryOptions> captured, Guid id, string partitionKey)
    {
        var options = captured.ShouldHaveSingleItem();
        options.DeduplicationId.ShouldBe(id.ToString("N"));
        options.PartitionKey.ShouldBe(partitionKey);
        options.Headers["lab-message-id"].ShouldBe(id.ToString("D"));
    }

    private static async Task<InventoryOutboxRecord> GivenPendingMessage(InventoryPostgresDatabase database)
    {
        var productId = Guid.CreateVersion7();
        var message = new ProductStockDecreasedIntegrationEvent(Guid.CreateVersion7(), productId, 2, 3);
        var row = new InventoryOutboxRecord
        {
            Id = Guid.CreateVersion7(), PartitionKey = productId.ToString("N"), MessageType = message.GetType().Name,
            Data = JsonSerializer.Serialize(message), OccurredOn = message.OccurredOn,
            CreatedOn = DateTime.UtcNow.AddMinutes(-1), NextAttemptAt = DateTime.UtcNow.AddMinutes(-1)
        };
        await using var context = database.CreateContext();
        context.OutboxMessages.Add(row);
        await context.SaveChangesAsync();
        return row;
    }

    private static ServiceProvider GivenRelayServices(InventoryPostgresDatabase database, RecordingPublisher publisher)
        => new ServiceCollection()
            .AddDbContext<InventoryDbContext>(options => options.UseNpgsql(database.ConnectionString))
            .AddSingleton<IIntegrationEventPublisher>(publisher)
            .BuildServiceProvider();

    private static async Task<CompletedReservation> GivenCompletedReservation(
        InventoryPostgresDatabase database, int initialStock, int quantity)
    {
        var item = new InventoryItem(Guid.CreateVersion7(), initialStock);
        await using var context = database.CreateContext();
        context.InventoryItems.Add(item);
        await context.SaveChangesAsync(TestContext.Current.CancellationToken);
        var input = new ReserveInventoryInput(Guid.CreateVersion7(), item.ProductId, quantity);
        var outcome = await new ReserveInventoryUseCase(new PostgresInventoryReservationRepository(context))
            .ExecuteAsync(input, TestContext.Current.CancellationToken);
        outcome.IsSuccess.ShouldBeTrue();
        outcome.WasAlreadyProcessed.ShouldBeFalse();
        var operation = await context.ReservationOperations.AsNoTracking()
            .SingleAsync(row => row.OperationId == input.OperationId, TestContext.Current.CancellationToken);
        operation.CompletedAt.ShouldNotBeNull();
        return new CompletedReservation(input, outcome, operation.CompletedAt.Value);
    }

    private static async Task GivenReservationWasPublishedAndPurged(InventoryPostgresDatabase database,
        ServiceProvider services, RecordingPublisher publisher, Guid operationId, int retentionDays)
    {
        await WhenRelaying(services, cancellationToken: TestContext.Current.CancellationToken);
        publisher.Deliveries.ShouldHaveSingleItem().MessageId.ShouldBe(operationId);
        await using var context = database.CreateContext();
        var row = await context.OutboxMessages.AsNoTracking()
            .SingleAsync(message => message.Id == operationId, TestContext.Current.CancellationToken);
        row.PublishedAt.ShouldNotBeNull();
        var expiredAt = DateTime.UtcNow.AddDays(-retentionDays - 1);
        (await context.OutboxMessages.Where(message => message.Id == operationId && message.PublishedAt != null)
            .ExecuteUpdateAsync(setters => setters.SetProperty(message => message.PublishedAt, expiredAt),
                TestContext.Current.CancellationToken)).ShouldBe(1);
        await WhenRelaying(services,
            new InventoryOutboxRelayOptions(false, InventoryOutboxRetentionMode.PublishedForDays, retentionDays),
            TestContext.Current.CancellationToken);
        (await context.OutboxMessages.AnyAsync(message => message.Id == operationId,
            TestContext.Current.CancellationToken)).ShouldBeFalse();
        publisher.Deliveries.Count.ShouldBe(1);
    }

    private static async Task GivenReservationOutboxRowIsMissing(InventoryPostgresDatabase database, Guid operationId)
    {
        await using var context = database.CreateContext();
        (await context.OutboxMessages.Where(message => message.Id == operationId)
            .ExecuteDeleteAsync(TestContext.Current.CancellationToken)).ShouldBe(1);
    }

    private static async Task<(ReserveInventoryOutput Outcome, int StagedMessages)> WhenReplayingReservationAndRelaying(
        InventoryPostgresDatabase database, ServiceProvider services, ReserveInventoryInput input)
    {
        await using var context = database.CreateContext();
        var outcome = await new ReserveInventoryUseCase(new PostgresInventoryReservationRepository(context))
            .ExecuteAsync(input, TestContext.Current.CancellationToken);
        var stagedMessages = await context.OutboxMessages.CountAsync(TestContext.Current.CancellationToken);
        await WhenRelaying(services, cancellationToken: TestContext.Current.CancellationToken);
        return (outcome, stagedMessages);
    }

    private static async Task ThenReplayShouldNotStageOrPublish(InventoryPostgresDatabase database,
        RecordingPublisher publisher, CompletedReservation original,
        (ReserveInventoryOutput Outcome, int StagedMessages) replay, int expectedStock, int expectedPublications)
    {
        replay.Outcome.ShouldBe(original.Outcome with { WasAlreadyProcessed = true });
        replay.StagedMessages.ShouldBe(0);
        publisher.Deliveries.Count.ShouldBe(expectedPublications);
        publisher.Messages.Count.ShouldBe(expectedPublications);
        publisher.Deliveries.ShouldAllBe(delivery => delivery.MessageId == original.Input.OperationId);
        await using var context = database.CreateContext();
        (await context.InventoryItems.Where(item => item.ProductId == original.Input.ProductId)
            .Select(item => item.Stock).SingleAsync(TestContext.Current.CancellationToken)).ShouldBe(expectedStock);
        var operations = await context.ReservationOperations.AsNoTracking().ToListAsync(TestContext.Current.CancellationToken);
        var operation = operations.ShouldHaveSingleItem();
        operation.OperationId.ShouldBe(original.Input.OperationId);
        operation.ProductId.ShouldBe(original.Input.ProductId);
        operation.Quantity.ShouldBe(original.Input.Quantity);
        operation.IsSuccess.ShouldBe(true);
        operation.RemainingStock.ShouldBe(original.Outcome.RemainingStock);
        operation.FailureReason.ShouldBeNull();
        operation.CompletedAt.ShouldBe(original.CompletedAt);
        (await context.OutboxMessages.CountAsync(TestContext.Current.CancellationToken)).ShouldBe(0);
    }

    private static Task WhenRelaying(ServiceProvider services, InventoryOutboxRelayOptions? options = null, CancellationToken cancellationToken = default)
        => new InventoryIntegrationOutboxRelay(services.GetRequiredService<IServiceScopeFactory>(),
            options ?? new InventoryOutboxRelayOptions(false, InventoryOutboxRetentionMode.RetainAll, null),
            NullLogger<InventoryIntegrationOutboxRelay>.Instance).RelayBatchAsync(cancellationToken);

    private static async Task WhenRelayingWithRetry(InventoryPostgresDatabase database, ServiceProvider services, Guid id)
    {
        await WhenRelaying(services);
        await MakeRetryDue(database, id);
        await WhenRelaying(services);
    }

    private static async Task WhenRelayingThroughFiveFailures(InventoryPostgresDatabase database, ServiceProvider services, Guid id)
    {
        for (var attempt = 0; attempt < 5; attempt++)
        {
            await MakeRetryDue(database, id);
            await WhenRelaying(services);
        }

        await WhenRelaying(services);
    }

    private static Task WhenTwoRelaysRunConcurrently(ServiceProvider services)
        => Task.WhenAll(WhenRelaying(services), WhenRelaying(services));

    private static async Task<Exception?> WhenRelayingWithCancellation(ServiceProvider services)
    {
        using var cancellation = new CancellationTokenSource();
        cancellation.Cancel();
        return await Record.ExceptionAsync(() => WhenRelaying(services, cancellationToken: cancellation.Token));
    }

    private static async Task MakeRetryDue(InventoryPostgresDatabase database, Guid id)
    {
        await using var context = database.CreateContext();
        await context.OutboxMessages.Where(row => row.Id == id)
            .ExecuteUpdateAsync(setters => setters.SetProperty(row => row.NextAttemptAt, DateTime.UtcNow.AddMinutes(-1)));
    }

    private static async Task ThenRetriedDeliveryShouldBeStable(InventoryPostgresDatabase database, RecordingPublisher publisher, InventoryOutboxRecord source)
    {
        var deliveries = publisher.Deliveries.ToArray();
        deliveries.Length.ShouldBe(2);
        deliveries.ShouldAllBe(delivery => delivery.MessageId == source.Id && delivery.PartitionKey == source.PartitionKey);
        publisher.Messages.ShouldAllBe(message => message.OccurredOn == source.OccurredOn);
        await using var context = database.CreateContext();
        var row = await context.OutboxMessages.SingleAsync(message => message.Id == source.Id);
        row.Attempts.ShouldBe(2);
        row.PublishedAt.ShouldNotBeNull();
        row.LastError.ShouldBeNull();
        row.LockId.ShouldBeNull();
    }

    private static async Task ThenMessageShouldBeParked(InventoryPostgresDatabase database, RecordingPublisher publisher, Guid id)
    {
        publisher.Deliveries.Count.ShouldBe(5);
        await using var context = database.CreateContext();
        var row = await context.OutboxMessages.SingleAsync(message => message.Id == id);
        row.Attempts.ShouldBe(5);
        row.ParkedAt.ShouldNotBeNull();
        row.PublishedAt.ShouldBeNull();
        row.LockId.ShouldBeNull();
        row.LastError.ShouldNotBeNull();
        row.LastError.Length.ShouldBeLessThanOrEqualTo(4000);
    }

    private static async Task<(Guid Expired, Guid Recent, Guid Parked)> GivenRetentionRows(InventoryPostgresDatabase database)
    {
        var expired = await GivenPendingMessage(database);
        var recent = await GivenPendingMessage(database);
        var parked = await GivenPendingMessage(database);
        await using var context = database.CreateContext();
        await context.OutboxMessages.Where(row => row.Id == expired.Id)
            .ExecuteUpdateAsync(setters => setters.SetProperty(row => row.PublishedAt, DateTime.UtcNow.AddDays(-8)));
        await context.OutboxMessages.Where(row => row.Id == recent.Id)
            .ExecuteUpdateAsync(setters => setters.SetProperty(row => row.PublishedAt, DateTime.UtcNow.AddDays(-1)));
        await context.OutboxMessages.Where(row => row.Id == parked.Id)
            .ExecuteUpdateAsync(setters => setters.SetProperty(row => row.ParkedAt, DateTime.UtcNow.AddDays(-8)));
        return (expired.Id, recent.Id, parked.Id);
    }

    private static async Task ThenRetentionShouldKeepRecentAndUnpublished(InventoryPostgresDatabase database, Guid expired, Guid recent, Guid parked)
    {
        await using var context = database.CreateContext();
        (await context.OutboxMessages.AnyAsync(row => row.Id == expired)).ShouldBeFalse();
        (await context.OutboxMessages.AnyAsync(row => row.Id == recent)).ShouldBeTrue();
        (await context.OutboxMessages.AnyAsync(row => row.Id == parked)).ShouldBeTrue();
    }

    private static async Task ThenOneDeliveryShouldBePublished(InventoryPostgresDatabase database, RecordingPublisher publisher, Guid id)
    {
        publisher.Deliveries.ShouldHaveSingleItem().MessageId.ShouldBe(id);
        await using var context = database.CreateContext();
        (await context.OutboxMessages.SingleAsync(row => row.Id == id)).PublishedAt.ShouldNotBeNull();
    }

    private static async Task ThenCancelledBatchShouldLeaveMessagePending(InventoryPostgresDatabase database, RecordingPublisher publisher, Guid id, Exception? error)
    {
        error.ShouldBeAssignableTo<OperationCanceledException>();
        publisher.Deliveries.ShouldBeEmpty();
        await using var context = database.CreateContext();
        var row = await context.OutboxMessages.SingleAsync(message => message.Id == id);
        row.Attempts.ShouldBe(0);
        row.LockId.ShouldBeNull();
        row.PublishedAt.ShouldBeNull();
    }

    private static async Task<InventoryOutboxRecord> GivenExpiredLease(InventoryPostgresDatabase database)
    {
        var row = await GivenPendingMessage(database);
        await using var context = database.CreateContext();
        await context.OutboxMessages.Where(message => message.Id == row.Id)
            .ExecuteUpdateAsync(setters => setters.SetProperty(message => message.LockId, Guid.CreateVersion7())
                .SetProperty(message => message.LockedUntil, DateTime.UtcNow.AddMinutes(-1)));
        return row;
    }

    private sealed record CompletedReservation(ReserveInventoryInput Input, ReserveInventoryOutput Outcome, DateTime CompletedAt);

    private sealed class RecordingPublisher(int failures = 0) : IIntegrationEventPublisher
    {
        private int attempts;
        public ConcurrentQueue<IIntegrationEvent> Messages { get; } = new();
        public ConcurrentQueue<IntegrationMessageDelivery> Deliveries { get; } = new();
        public Task PublishAsync(IIntegrationEvent integrationEvent) => throw new NotSupportedException();

        public Task PublishAsync(IIntegrationEvent integrationEvent, IntegrationMessageDelivery delivery)
        {
            this.Messages.Enqueue(integrationEvent);
            this.Deliveries.Enqueue(delivery);
            return Interlocked.Increment(ref this.attempts) <= failures
                ? Task.FromException(new InvalidOperationException("Simulated transport failure."))
                : Task.CompletedTask;
        }
    }
}
