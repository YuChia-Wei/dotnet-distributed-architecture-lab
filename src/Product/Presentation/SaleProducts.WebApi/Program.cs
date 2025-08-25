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

// OpenTelemetry: tracing, metrics (CPU/Memory), logging
var serviceName = builder.Environment.ApplicationName;
builder.Services.AddOpenTelemetry()
       .ConfigureResource(r => r.AddService(serviceName))
       .WithTracing(t => t
                         .AddAspNetCoreInstrumentation()
                         .AddHttpClientInstrumentation()
                         .AddOtlpExporter())
       .WithMetrics(m => m
                         .AddAspNetCoreInstrumentation()
                         .AddHttpClientInstrumentation()
                         .AddRuntimeInstrumentation()
                         .AddProcessInstrumentation()
                         .AddOtlpExporter());

builder.Logging.AddOpenTelemetry(o =>
{
    o.IncludeScopes = true;
    o.ParseStateValues = true;
    o.IncludeFormattedMessage = true;
    o.AddOtlpExporter();
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