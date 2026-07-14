// See https://aka.ms/new-console-template for more information

using Confluent.Kafka.Extensions.OpenTelemetry;
using Lab.BuildingBlocks.Integrations.Configuration;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using OpenTelemetry.Logs;
using OpenTelemetry.Metrics;
using OpenTelemetry.Trace;
using Wolverine;
using Wolverine.Kafka;
using Wolverine.RabbitMQ;

var configuration = new ConfigurationManager()
    .AddEnvironmentVariables()
    .AddCommandLine(args)
    .Build();
var messaging = MessagingTransportOptions.FromConfiguration(configuration);

var builder = Host.CreateDefaultBuilder(args)
                  .ConfigureServices((ctx, services) =>
                  {
                      services.AddOpenTelemetry()
                              .WithLogging(loggerProviderBuilder =>
                              {
                                  loggerProviderBuilder.AddOtlpExporter();
                              })
                              .WithTracing(tracerProviderBuilder =>
                              {
                                  tracerProviderBuilder
                                      // .AddHttpClientInstrumentation()
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
                  })
                  .UseWolverine(opts =>
                  {
                      if (messaging.Profile == MessagingTransportProfile.InMemory)
                      {
                          opts.StubAllExternalTransports();
                      }
                      else if (messaging.Profile == MessagingTransportProfile.Kafka)
                      {
                          opts.UseKafka(messaging.GetRequiredKafkaConnectionString())
                              .AutoProvision();

                          opts.ListenToKafkaTopic("orders.integration.events")
                              .UseDurableInbox();
                      }
                      else
                      {
                          opts.UseRabbitMq(messaging.GetRequiredRabbitMqUri())
                              .AutoProvision();

                          opts.ListenToRabbitQueue("orders.integration.events")
                              .UseDurableInbox()
                              .ListenerCount(4);
                      }

                      opts.Discovery.IncludeAssembly(typeof(Program).Assembly);
                  });

await builder.RunConsoleAsync(); // Ctrl+C 可優雅關閉
