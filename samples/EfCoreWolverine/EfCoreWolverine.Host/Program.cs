using System.Text.Json;
using EfCoreWolverine.Infrastructure;
using InventoryControl.Domains;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Wolverine;

namespace EfCoreWolverine.Host;

public static class Program
{
    /// <summary>Runs setup, ingress, inspection, or the consumer; seed is separate demo setup without a stock event.</summary>
    public static async Task Main(string[] args)
    {
        var configuration = new ConfigurationBuilder().SetBasePath(AppContext.BaseDirectory)
            .AddJsonFile("appsettings.json").AddEnvironmentVariables().AddCommandLine(args).Build();
        var settings = SampleSettings.FromConfiguration(configuration);
        var mode = configuration["mode"] ?? "consume";

        if (mode is "seed" or "inspect")
        {
            await using var db = new InventoryDbContext(new DbContextOptionsBuilder<InventoryDbContext>()
                .UseNpgsql(settings.ConnectionString).Options);
            if (mode == "seed")
            {
                await db.Database.MigrateAsync();
                var stock = int.Parse(configuration["stock"] ?? "10");
                ArgumentOutOfRangeException.ThrowIfNegative(stock);
                var item = new InventoryItem(Guid.NewGuid(), stock);
                db.InventoryItems.Add(item);
                await db.SaveChangesAsync();
                Console.WriteLine(JsonSerializer.Serialize(new { item.Id, item.ProductId, item.Stock }));
            }
            else
            {
                var id = Guid.Parse(configuration["id"] ?? throw new ArgumentException("Supply --id."));
                var item = await db.InventoryItems.AsNoTracking().SingleOrDefaultAsync(x => x.Id == id);
                Console.WriteLine(JsonSerializer.Serialize(item is null ? null : new { item.Id, item.ProductId, item.Stock }));
            }
            return;
        }

        if (mode == "send")
        {
            var id = Guid.Parse(configuration["id"] ?? throw new ArgumentException("Supply --id."));
            var quantity = int.Parse(configuration["quantity"] ?? "1");
            ArgumentOutOfRangeException.ThrowIfNegativeOrZero(quantity);
            using var sender = SampleHost.BuildSender(settings);
            await sender.StartAsync();
            await using var scope = sender.Services.CreateAsyncScope();
            await scope.ServiceProvider.GetRequiredService<IMessageBus>()
                .PublishAsync(new DecreaseStockRequested(id, quantity),
                    new DeliveryOptions { PartitionKey = id.ToString("N") });
            Console.WriteLine("Kafka accepted the request. Use inspect to observe asynchronous processing.");
            await sender.StopAsync();
            return;
        }

        if (mode != "consume") throw new ArgumentException("Use --mode seed, consume, send, or inspect.");
        using var consumer = SampleHost.BuildConsumer(settings);
        await consumer.RunAsync();
    }
}
