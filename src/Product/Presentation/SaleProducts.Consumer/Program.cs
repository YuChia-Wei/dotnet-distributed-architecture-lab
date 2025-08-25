// See https://aka.ms/new-console-template for more information

using Microsoft.Extensions.Hosting;
using Wolverine;
using Wolverine.Kafka;
using Wolverine.RabbitMQ;
using OpenTelemetry.Logs;
using OpenTelemetry.Metrics;
using OpenTelemetry.Resources;
using OpenTelemetry.Trace;

var queueServiceUri = Environment.GetEnvironmentVariable("QUEUE_SERVICE") ?? string.Empty;
ArgumentNullException.ThrowIfNull(queueServiceUri);
var brokerConnectionString = Environment.GetEnvironmentVariable("BrokerConnectionString") ?? string.Empty;
ArgumentNullException.ThrowIfNull(brokerConnectionString);

var builder = Host.CreateDefaultBuilder(args)
                  .ConfigureServices((ctx, services) =>
                  {
                      var serviceName = ctx.HostingEnvironment.ApplicationName;
                      services.AddOpenTelemetry()
                          .ConfigureResource(r => r.AddService(serviceName))
                          .WithTracing(t => t
                              .AddHttpClientInstrumentation()
                              .AddOtlpExporter())
                          .WithMetrics(m => m
                              .AddHttpClientInstrumentation()
                              .AddRuntimeInstrumentation()
                              .AddProcessInstrumentation()
                              .AddOtlpExporter());
                  })
                  .ConfigureLogging((ctx, logging) =>
                  {
                      logging.AddOpenTelemetry(o =>
                      {
                          o.IncludeScopes = true;
                          o.ParseStateValues = true;
                          o.IncludeFormattedMessage = true;
                          o.AddOtlpExporter();
                      });
                  })
                  .UseWolverine(opts =>
                  {
                      if (queueServiceUri.Equals("Kafka", StringComparison.OrdinalIgnoreCase))
                      {
                          opts.UseKafka(brokerConnectionString)
                              .AutoProvision();

                          opts.ListenToKafkaTopic("orders")
                              .UseDurableInbox();
                      }
                      else if (queueServiceUri.Equals("RabbitMQ", StringComparison.OrdinalIgnoreCase))
                      {
                          opts.UseRabbitMq(new Uri(brokerConnectionString))
                              .AutoProvision();
                          opts.ListenToRabbitQueue("orders")
                              .UseDurableInbox()
                              .ListenerCount(4);
                      }

                      opts.Discovery.IncludeAssembly(typeof(Program).Assembly);
                  });

await builder.RunConsoleAsync(); // Ctrl+C 可優雅關閉
