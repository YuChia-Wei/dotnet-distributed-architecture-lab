using System.Collections.Concurrent;
using System.Text;
using System.Text.Json;
using Confluent.Kafka;
using EfCoreWolverine.Application;
using EfCoreWolverine.Host;
using EfCoreWolverine.Infrastructure;
using InventoryControl.Domains;
using Lab.BoundedContextContracts.Inventory.IntegrationEvents;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Npgsql;
using Wolverine;
using Wolverine.ErrorHandling;

namespace EfCoreWolverine.Tests;

/// <summary>Opt-in real PostgreSQL + Kafka fixture; never substitutes an in-memory transport.</summary>
public sealed class MessagingFixture : IAsyncLifetime
{
    private IHost? consumer;
    private IProducer<string, byte[]>? producer;
    private readonly List<Guid> seededIds = [];
    public SampleSettings Settings { get; private set; } = null!;
    public FlushProbe Probe { get; } = new();

    public async ValueTask InitializeAsync()
    {
        if (!ExternalMessagingFactAttribute.Enabled) return;
        var suffix = Guid.NewGuid().ToString("N");
        Settings = new(Environment.GetEnvironmentVariable(ExternalMessagingFactAttribute.PostgresVariable)!,
            Environment.GetEnvironmentVariable(ExternalMessagingFactAttribute.KafkaVariable)!,
            "ef-sample-requests-" + suffix, "ef-sample-events-" + suffix,
            "ef-sample-group-" + suffix, "ef_sample_" + suffix);
        await using (var db = NewDb()) await db.Database.MigrateAsync(TestContext.Current.CancellationToken);

        consumer = SampleHost.BuildConsumer(Settings, services =>
        {
            services.AddSingleton(Probe);
            services.AddScoped<IStockEventPublisher, FlushProbePublisher>();
        }, options => options.OnException<InjectedAfterFlushException>().MoveToErrorQueue());
        using var startup = new CancellationTokenSource(TimeSpan.FromSeconds(45));
        try
        {
            await consumer.StartAsync(startup.Token);
            producer = new ProducerBuilder<string, byte[]>(new ProducerConfig
            {
                BootstrapServers = Settings.KafkaBootstrapServers,
                MessageTimeoutMs = 15000
            }).Build();
        }
        catch
        {
            await DisposeAsync();
            throw;
        }
    }

    public InventoryDbContext NewDb() => new(new DbContextOptionsBuilder<InventoryDbContext>()
        .UseNpgsql(Settings.ConnectionString).Options);

    public async Task<InventoryItem> SeedAsync(int stock)
    {
        var item = new InventoryItem(Guid.NewGuid(), stock);
        await using var db = NewDb();
        db.InventoryItems.Add(item);
        await db.SaveChangesAsync(TestContext.Current.CancellationToken);
        seededIds.Add(item.Id);
        return item;
    }

    /// <summary>Uses identical envelope identity and payload for a genuine default-mapper Kafka redelivery.</summary>
    public Task SendAsync(DecreaseStockRequested request, Guid envelopeId)
    {
        var type = new Envelope(request).MessageType!;
        return producer!.ProduceAsync(Settings.RequestTopic, new Message<string, byte[]>
        {
            Key = request.InventoryItemId.ToString("N"),
            Value = JsonSerializer.SerializeToUtf8Bytes(request),
            Headers = new Headers
            {
                { "id", Encoding.UTF8.GetBytes(envelopeId.ToString()) },
                { "message-type", Encoding.UTF8.GetBytes(type) },
                { "content-type", Encoding.UTF8.GetBytes("application/json") }
            }
        }, TestContext.Current.CancellationToken);
    }

    public async Task<int> StockAsync(Guid id)
    {
        await using var db = NewDb();
        return await db.InventoryItems.Where(x => x.Id == id).Select(x => x.Stock)
            .SingleAsync(TestContext.Current.CancellationToken);
    }

    public async Task<string?> InboxStatusAsync(Guid id)
    {
        await using var connection = new NpgsqlConnection(Settings.ConnectionString);
        await connection.OpenAsync(TestContext.Current.CancellationToken);
        await using var command = new NpgsqlCommand(
            $"SELECT status FROM {Settings.MessageSchema}.wolverine_incoming_envelopes WHERE id = @id", connection);
        command.Parameters.AddWithValue("id", id);
        return (await command.ExecuteScalarAsync(TestContext.Current.CancellationToken))?.ToString();
    }

    public async Task<int> OutboxCountAsync()
    {
        await using var connection = new NpgsqlConnection(Settings.ConnectionString);
        await connection.OpenAsync(TestContext.Current.CancellationToken);
        await using var command = new NpgsqlCommand(
            $"SELECT count(*)::int FROM {Settings.MessageSchema}.wolverine_outgoing_envelopes", connection);
        return (int)(await command.ExecuteScalarAsync(TestContext.Current.CancellationToken))!;
    }

    public IConsumer<string, byte[]> EventConsumer()
    {
        var observer = new ConsumerBuilder<string, byte[]>(new ConsumerConfig
        {
            BootstrapServers = Settings.KafkaBootstrapServers,
            GroupId = "assert-events-" + Guid.NewGuid().ToString("N"),
            AutoOffsetReset = AutoOffsetReset.Earliest,
            EnableAutoCommit = false
        }).Build();
        observer.Subscribe(Settings.EventTopic);
        return observer;
    }

    /// <summary>Cleans up only this fixture's rows, message schema and topics, preserving the database and business schema.</summary>
    public async ValueTask DisposeAsync()
    {
        if (!ExternalMessagingFactAttribute.Enabled || Settings is null) return;
        producer?.Dispose();
        if (consumer is not null)
        {
            using var shutdown = new CancellationTokenSource(TimeSpan.FromSeconds(15));
            try { await consumer.StopAsync(shutdown.Token); }
            finally { consumer.Dispose(); }
        }
        await using var db = NewDb();
        await db.InventoryItems.Where(x => seededIds.Contains(x.Id)).ExecuteDeleteAsync(CancellationToken.None);
        await using var connection = new NpgsqlConnection(Settings.ConnectionString);
        await connection.OpenAsync(CancellationToken.None);
        var schema = new NpgsqlCommandBuilder().QuoteIdentifier(Settings.MessageSchema);
        await using var cleanup = new NpgsqlCommand($"DROP SCHEMA IF EXISTS {schema} CASCADE", connection);
        await cleanup.ExecuteNonQueryAsync(CancellationToken.None);
        using var admin = new AdminClientBuilder(new AdminClientConfig { BootstrapServers = Settings.KafkaBootstrapServers }).Build();
        await admin.DeleteTopicsAsync([Settings.RequestTopic, Settings.EventTopic]);
    }
}

public sealed class FlushProbe
{
    public ConcurrentDictionary<Guid, bool> RejectAfterFlush { get; } = new();
    public ConcurrentDictionary<Guid, int> Calls { get; } = new();
    public ConcurrentDictionary<Guid, TaskCompletionSource<bool>> Flushed { get; } = new();
    public TaskCompletionSource<bool> For(Guid id) => Flushed.GetOrAdd(id,
        _ => new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously));
}

public sealed class InjectedAfterFlushException : Exception;

/// <summary>Test-only fault seam: force SQL inside the actual middleware transaction, then optionally fail.</summary>
public sealed class FlushProbePublisher(InventoryDbContext db, IMessageContext messages, FlushProbe probe)
    : IStockEventPublisher
{
    public async Task PublishAsync(ProductStockDecreasedIntegrationEvent message, CancellationToken cancellationToken)
    {
        if (db.Database.CurrentTransaction is null)
            throw new InvalidOperationException("The Repository/publisher context was not enrolled in Eager middleware.");
        probe.Calls.AddOrUpdate(message.InventoryItemId, 1, (_, count) => count + 1);
        await new WolverineStockEventPublisher(messages).PublishAsync(message, cancellationToken);
        await db.SaveChangesAsync(cancellationToken);
        probe.For(message.InventoryItemId).TrySetResult(true);
        if (probe.RejectAfterFlush.ContainsKey(message.InventoryItemId)) throw new InjectedAfterFlushException();
    }
}
