// See https://aka.ms/new-console-template for more information

using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Hosting;
using Wolverine;
using Wolverine.Kafka;
using Wolverine.RabbitMQ;

var builder = Host.CreateDefaultBuilder(args)
    .UseWolverine((context, opts) =>
    {
        var queueService = context.Configuration.GetValue<string>("QUEUE_SERVICE");

        if ("Kafka".Equals(queueService, StringComparison.OrdinalIgnoreCase))
        {
            var kafkaConnectionString = context.Configuration.GetConnectionString("KafkaBroker");
            opts.UseKafka(kafkaConnectionString!);
            opts.ListenToKafkaTopic("orders").UseDurableInbox();
        }
        else
        {
            var rabbitMqConnectionString = context.Configuration.GetConnectionString("MessageBroker");
            opts.UseRabbitMq(new Uri(rabbitMqConnectionString!)).AutoProvision();
            opts.ListenToRabbitQueue("orders")
                .UseDurableInbox()
                .ListenerCount(4);
        }

        opts.ApplicationAssembly = typeof(Program).Assembly;
    });

await builder.RunConsoleAsync(); // Ctrl+C 可優雅關閉