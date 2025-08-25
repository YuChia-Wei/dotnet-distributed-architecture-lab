using Lab.BuildingBlocks.Domains;
using Lab.BuildingBlocks.Integrations;
using OpenTelemetry.Logs;
using OpenTelemetry.Metrics;
using OpenTelemetry.Resources;
using OpenTelemetry.Trace;
using SaleProducts.Applications;
using SaleProducts.Infrastructure;
using Scalar.AspNetCore;
using Wolverine;
using Wolverine.Kafka;
using Wolverine.RabbitMQ;
using ServiceCollectionExtensions = SaleProducts.Applications.ServiceCollectionExtensions;

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

        opts.Publish(rule =>
        {
            rule.MessagesImplementing<IIntegrationEvent>();
            rule.ToKafkaTopic("products")
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
            rule.ToRabbitQueue("products")
                .UseDurableOutbox();
        });
    }

    // Publish domain events locally
    opts.PublishMessage<IDomainEvent>().Locally();

    // Discover services
    opts.Discovery.IncludeAssembly(typeof(ServiceCollectionExtensions).Assembly);
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
               .AddOtlpExporter();
       })
       .WithMetrics(meterProviderBuilder =>
       {
           meterProviderBuilder
               .AddRuntimeInstrumentation()
               // .AddHttpClientInstrumentation()
               .AddAspNetCoreInstrumentation()
               .AddProcessInstrumentation()
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