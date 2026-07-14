using Confluent.Kafka.Extensions.OpenTelemetry;
using InventoryControl.Applications;
using InventoryControl.Infrastructure;
using InventoryControl.Infrastructure.Messaging;
using Lab.BuildingBlocks.Domains;
using Lab.BuildingBlocks.Integrations;
using Lab.BuildingBlocks.Integrations.Configuration;
using OpenTelemetry.Logs;
using OpenTelemetry.Metrics;
using OpenTelemetry.Trace;
using Scalar.AspNetCore;
using Wolverine;
using Wolverine.Kafka;
using Wolverine.Postgresql;
using Wolverine.RabbitMQ;
using ServiceCollectionExtensions = InventoryControl.Applications.ServiceCollectionExtensions;

var builder = WebApplication.CreateBuilder(args);
var messaging = MessagingTransportOptions.FromConfiguration(builder.Configuration);

builder.Host.UseWolverine(opts =>
{
    InventoryReservationFailurePolicy.Configure(opts);

    if (messaging.Profile == MessagingTransportProfile.InMemory)
    {
        opts.StubAllExternalTransports();
        opts.LocalQueue("inventory-requests");
        opts.PublishMessage<IIntegrationEvent>().ToLocalQueue("inventory-integration-events");
    }
    else if (messaging.Profile == MessagingTransportProfile.Kafka)
    {
        ConfigurePostgresqlPersistence(opts, builder.Configuration);

        // Configure Kafka
        opts.UseKafka(messaging.GetRequiredKafkaConnectionString())
            .AutoProvision();

        // 監聽跨服務間的要求資料
        opts.ListenToKafkaTopic("inventory.requests")
            .ProcessInline()
            .ListenerCount(3)
            .UseDurableInbox();

        // Request replies use Wolverine's reply endpoint carried by the request envelope.
        // Do not broadcast response contracts to a second integration topic.

        // 設定整合事件的發布通道
        opts.Publish(rule =>
        {
            rule.MessagesImplementing<IIntegrationEvent>();
            rule.ToKafkaTopic("inventory.integration.events")
                .UseDurableOutbox();
        });
    }
    else
    {
        ConfigurePostgresqlPersistence(opts, builder.Configuration);

        // Configure RabbitMQ
        opts.UseRabbitMq(messaging.GetRequiredRabbitMqUri())
            .AutoProvision();

        opts.ListenToRabbitQueue("inventory.requests")
            .ProcessInline()
            .ListenerCount(3)
            .UseDurableInbox();

        opts.Publish(rule =>
        {
            rule.MessagesImplementing<IIntegrationEvent>();
            rule.ToRabbitQueue("inventory.integration.events")
                .UseDurableOutbox();
        });
    }

    // Publish domain events locally
    opts.PublishMessage<IDomainEvent>().Locally();

    // Discover services
    opts.Discovery.IncludeAssembly(typeof(ServiceCollectionExtensions).Assembly);
    opts.Discovery.IncludeAssembly(typeof(Program).Assembly);
});

static void ConfigurePostgresqlPersistence(WolverineOptions options, IConfiguration configuration)
{
    var connectionString = configuration.GetConnectionString("DefaultConnection")
        ?? throw new InvalidOperationException("ConnectionStrings:DefaultConnection is required for Wolverine message persistence.");
    options.PersistMessagesWithPostgresql(connectionString, "wolverine_messages");
}

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();

// Learn more about configuring OpenAPI at https://aka.ms/aspnet/openapi
builder.Services.AddOpenApi();

// domain core DI
builder.Services.AddApplicationServices();
builder.Services.AddInfrastructureServices(builder.Configuration);

builder.Services.AddOpenTelemetry()
       .WithLogging(loggerProviderBuilder =>
       {
           loggerProviderBuilder.AddOtlpExporter();
       })
       .WithTracing(tracerProviderBuilder =>
       {
           tracerProviderBuilder
               // .AddHttpClientInstrumentation()
               .AddAspNetCoreInstrumentation()
               // .AddEntityFrameworkCoreInstrumentation()
               .AddSource("Wolverine")
               .AddRabbitMQInstrumentation()
               .AddConfluentKafkaInstrumentation()
               .AddOtlpExporter();
       })
       .WithMetrics(meterProviderBuilder =>
       {
           meterProviderBuilder
               .AddRuntimeInstrumentation()
               // .AddHttpClientInstrumentation()
               .AddAspNetCoreInstrumentation()
               .AddProcessInstrumentation()
               .AddMeter("Wolverine")
               .AddOtlpExporter((exporterOptions, metricReaderOptions) =>
               {
                   var endpoint = Environment.GetEnvironmentVariable("OTEL_EXPORTER_OTLP_ENDPOINT");
                   exporterOptions.Endpoint = !string.IsNullOrWhiteSpace(endpoint)
                                                  ? new Uri(endpoint)
                                                  : new Uri("http://localhost:4317");

                   metricReaderOptions.PeriodicExportingMetricReaderOptions.ExportIntervalMilliseconds = 1000;
               });
       });

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.MapOpenApi()
       .CacheOutput();

    app.MapScalarApiReference();
}

app.UseHttpsRedirection();

app.UseAuthorization();

app.MapControllers();

app.Run();

/// <summary>
/// 測試專用的部分 Program 類別宣告。
/// </summary>
public partial class Program
{
}
