using Confluent.Kafka.Extensions.OpenTelemetry;
using InventoryControl.Applications;
using InventoryControl.Infrastructure;
using Lab.BuildingBlocks.Domains;
using Lab.BuildingBlocks.Integrations;
using OpenTelemetry.Logs;
using OpenTelemetry.Metrics;
using OpenTelemetry.Trace;
using Scalar.AspNetCore;
using Wolverine;
using Wolverine.Kafka;
using Wolverine.RabbitMQ;
using ServiceCollectionExtensions = InventoryControl.Applications.ServiceCollectionExtensions;

var builder = WebApplication.CreateBuilder(args);

builder.Host.UseWolverine(opts =>
{
    // Get the queue service type from environment variables
    var queueService = builder.Configuration.GetValue<string>("QUEUE_SERVICE");

    if ("Kafka".Equals(queueService, StringComparison.OrdinalIgnoreCase))
    {
        // Configure Kafka
        var kafkaConnectionString = builder.Configuration.GetConnectionString("KafkaBroker");
        opts.UseKafka(kafkaConnectionString!)
            .AutoProvision();

        // 監聽跨服務間的要求資料
        opts.ListenToKafkaTopic("inventory.requests")
            .ProcessInline()
            .ListenerCount(3)
            .UseDurableInbox();

        // 如果想把整合命令的回應也視為一種整合事件，可以這樣設定，wolverine 會在 request contract handler 完成處理並回應時，額外回應物件到這邊
        // opts.Publish(rule =>
        // {
        //     rule.MessagesImplementing<IInventoryResponseContract>();
        //     rule.ToKafkaTopic("inventory.responses")
        //         .UseDurableOutbox();
        // });

        // 設定整合事件的發布通道
        opts.Publish(rule =>
        {
            rule.MessagesImplementing<IIntegrationEvent>();
            rule.ToKafkaTopic("inventory.integration.events")
                .UseDurableOutbox();
        });
    }
    else // Default to RabbitMQ
    {
        // Configure RabbitMQ
        var rabbitMqConnectionString = builder.Configuration.GetConnectionString("MessageBroker");
        opts.UseRabbitMq(new Uri(rabbitMqConnectionString!))
            .AutoProvision();

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