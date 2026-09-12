using Confluent.Kafka;
using Lab.BuildingBlocks.Integrations.Diagnostics;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.DependencyInjection.Extensions;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using SaleOrders.Applications.Diagnostics;
using SaleOrders.Consumer.Diagnostics;
using SaleOrders.Consumer.Messaging;
using Wolverine;
using Wolverine.Kafka;

namespace SaleProducts.Tests;

/// <summary>Isolates each test session with one real Kafka topic, one group, and two hosts.</summary>
public sealed class KafkaParallelFixture : IAsyncLifetime
{
    public ParallelWorkProbeState State { get; } = new();
    public IHost Consumer { get; private set; } = null!;
    public IHost Producer { get; private set; } = null!;
    public string Topic { get; } = "parallel-probe-" + Guid.NewGuid().ToString("N");

    public async ValueTask InitializeAsync()
    {
        if (!KafkaParallelFactAttribute.Enabled) return;
        var bootstrap = Environment.GetEnvironmentVariable(KafkaParallelFactAttribute.BootstrapVariable)!;
        using var timeout = new CancellationTokenSource(TimeSpan.FromSeconds(45));
        this.Consumer = Host.CreateDefaultBuilder()
            .ConfigureLogging(logging => logging.SetMinimumLevel(LogLevel.Warning))
            .ConfigureServices(services =>
            {
                services.AddParallelWorkExamples();
                services.AddSingleton(this.State);
                services.RemoveAll<IParallelAuditWriter>();
                services.RemoveAll<IParallelStatisticsWriter>();
                services.AddScoped<IParallelAuditWriter, GatedAuditWriter>();
                services.AddScoped<IParallelStatisticsWriter, GatedStatisticsWriter>();
            })
            .UseWolverine(options =>
            {
                options.ServiceName = "parallel-consumer-" + this.Topic;
                options.Discovery.DisableConventionalDiscovery()
                    .IncludeType(typeof(WhenAllWorkHandler))
                    .IncludeType(typeof(IndependentAuditHandler))
                    .IncludeType(typeof(IndependentStatisticsHandler));
                options.ConfigureParallelWorkExamples();
                ConsumerFailurePolicy.Configure(options);
                options.UseKafka(bootstrap).AutoProvision().ConfigureConsumers(config =>
                {
                    config.GroupId = this.Topic;
                    config.AutoOffsetReset = AutoOffsetReset.Earliest;
                });
                options.ListenToKafkaTopic(this.Topic).EnableNativeDeadLetterQueue();
            }).Build();
        try
        {
            await this.Consumer.StartAsync(timeout.Token);
            this.Producer = Host.CreateDefaultBuilder()
                .ConfigureLogging(logging => logging.SetMinimumLevel(LogLevel.Warning))
                .UseWolverine(options =>
                {
                    options.ServiceName = "parallel-producer-" + this.Topic;
                    options.Discovery.DisableConventionalDiscovery();
                    options.UseKafka(bootstrap).AutoProvision();
                    options.PublishMessage<WhenAllWorkRequested>().ToKafkaTopic(this.Topic).SendInline();
                    options.PublishMessage<IndependentWorkRequested>().ToKafkaTopic(this.Topic).SendInline();
                }).Build();
            await this.Producer.StartAsync(timeout.Token);
        }
        catch
        {
            await this.DisposeAsync();
            throw;
        }
    }

    public async ValueTask DisposeAsync()
    {
        foreach (var probe in this.State.Probes.Values) probe.ReleaseBoth();
        using var timeout = new CancellationTokenSource(TimeSpan.FromSeconds(15));
        foreach (var host in new[] { this.Producer, this.Consumer })
        {
            if (host is null) continue;
            try { await host.StopAsync(timeout.Token); }
            finally { host.Dispose(); }
        }
    }

    public async Task PublishAsync<T>(T message) where T : class
    {
        await using var scope = this.Producer.Services.CreateAsyncScope();
        await scope.ServiceProvider.GetRequiredService<IMessageBus>().PublishAsync(message);
    }
}
