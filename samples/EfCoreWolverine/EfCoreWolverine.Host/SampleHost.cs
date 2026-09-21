using Confluent.Kafka;
using EfCoreWolverine.Application;
using EfCoreWolverine.Infrastructure;
using InventoryControl.Domains;
using JasperFx;
using Lab.BoundedContextContracts.Inventory.IntegrationEvents;
using Lab.BuildingBlocks.Application;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Wolverine;
using Wolverine.EntityFrameworkCore;
using Wolverine.ErrorHandling;
using Wolverine.Kafka;
using Wolverine.Persistence;
using Wolverine.Postgresql;

namespace EfCoreWolverine.Host;

public static class SampleHost
{
    /// <summary>Builds the demo with one scoped EF context discovered through UseCase/Repository constructors.</summary>
    /// <remarks>Automatic schema creation is for the isolated demo; production should provision schemas before startup.</remarks>
    public static IHost BuildConsumer(SampleSettings settings, Action<IServiceCollection>? customizeServices = null,
        Action<WolverineOptions>? customizeWolverine = null)
        => Microsoft.Extensions.Hosting.Host.CreateDefaultBuilder()
            .ConfigureServices(services =>
            {
                services.AddScoped<IAggregateRepository<InventoryItem, Guid>, EfInventoryRepository>();
                services.AddScoped<IDecreaseStockUseCase, DecreaseStockUseCase>();
                services.AddScoped<IStockEventPublisher, WolverineStockEventPublisher>();
                customizeServices?.Invoke(services);
            })
            .UseWolverine(options =>
            {
                options.ServiceName = settings.ConsumerGroup;
                options.Discovery.DisableConventionalDiscovery()
                    .IncludeType(typeof(DecreaseStockHandler))
                    .IncludeType(typeof(StockDecreasedObserver));

                options.Services.AddDbContextWithWolverineIntegration<InventoryDbContext>(
                    db => db.UseNpgsql(settings.ConnectionString));
                options.PersistMessagesWithPostgresql(settings.ConnectionString, settings.MessageSchema);
                options.UseEntityFrameworkCoreTransactions(TransactionMiddlewareMode.Eager);
                options.Policies.AutoApplyTransactions();

                options.AutoBuildMessageStorageOnStartup = AutoCreate.CreateOrUpdate;
                options.Durability.KeepAfterMessageHandling = TimeSpan.FromHours(1);
                options.OnException<DbUpdateConcurrencyException>().RetryWithCooldown(
                    TimeSpan.FromMilliseconds(100), TimeSpan.FromMilliseconds(500), TimeSpan.FromSeconds(1));

                options.UseKafka(settings.KafkaBootstrapServers).AutoProvision()
                    .ConfigureConsumers(config =>
                    {
                        config.GroupId = settings.ConsumerGroup;
                        config.AutoOffsetReset = AutoOffsetReset.Earliest;
                    });
                options.ListenToKafkaTopic(settings.RequestTopic).UseDurableInbox();
                options.ListenToKafkaTopic(settings.EventTopic).UseDurableInbox();
                options.PublishMessage<ProductStockDecreasedIntegrationEvent>().ToKafkaTopic(settings.EventTopic);
                options.Policies.UseDurableOutboxOnAllSendingEndpoints();
                customizeWolverine?.Invoke(options);
            }).Build();

    /// <summary>The demo ingress has no business-state transaction; it waits for Kafka's send result.</summary>
    public static IHost BuildSender(SampleSettings settings)
        => Microsoft.Extensions.Hosting.Host.CreateDefaultBuilder()
            .UseWolverine(options =>
            {
                options.ServiceName = settings.ConsumerGroup + "-sender";
                options.Discovery.DisableConventionalDiscovery();
                options.UseKafka(settings.KafkaBootstrapServers).AutoProvision();
                options.PublishMessage<DecreaseStockRequested>().ToKafkaTopic(settings.RequestTopic).SendInline();
            }).Build();
}
