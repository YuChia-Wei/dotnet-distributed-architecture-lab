// See https://aka.ms/new-console-template for more information

using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using OpenTelemetry.Logs;
using OpenTelemetry.Metrics;
using OpenTelemetry.Trace;
using Wolverine;
using Wolverine.Kafka;
using Wolverine.RabbitMQ;

var queueServiceUri = Environment.GetEnvironmentVariable("QUEUE_SERVICE") ?? string.Empty;
ArgumentNullException.ThrowIfNull(queueServiceUri);
var brokerConnectionString = Environment.GetEnvironmentVariable("BrokerConnectionString") ?? string.Empty;
ArgumentNullException.ThrowIfNull(brokerConnectionString);

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
                                      .AddOtlpExporter();
                              })
                              .WithMetrics(meterProviderBuilder =>
                              {
                                  meterProviderBuilder
                                      .AddRuntimeInstrumentation()
                                      // .AddHttpClientInstrumentation()
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
                  })
                  .UseWolverine(opts =>
                  {
                      if (queueServiceUri.Equals("Kafka", StringComparison.OrdinalIgnoreCase))
                      {
                          opts.UseKafka(brokerConnectionString)
                              .AutoProvision();
                          opts.ListenToKafkaTopic("products")
                              .UseDurableInbox();
                      }
                      else if (queueServiceUri.Equals("RabbitMQ", StringComparison.OrdinalIgnoreCase))
                      {
                          opts.UseRabbitMq(new Uri(brokerConnectionString))
                              .AutoProvision();
                          opts.ListenToRabbitQueue("products")
                              .UseDurableInbox()
                              .ListenerCount(4);
                      }

                      opts.Discovery.IncludeAssembly(typeof(Program).Assembly);
                  });

await builder.RunConsoleAsync(); // Ctrl+C 可優雅關閉