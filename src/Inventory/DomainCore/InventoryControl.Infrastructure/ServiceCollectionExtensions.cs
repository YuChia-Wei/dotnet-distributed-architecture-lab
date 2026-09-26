using InventoryControl.Infrastructure.Applications.Repositories;
using InventoryControl.Infrastructure.BuildingBlocks;
using Lab.BuildingBlocks.Application;
using Lab.BuildingBlocks.Domains;
using Lab.BuildingBlocks.Integrations;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using InventoryControl.Infrastructure.Persistence;
using Microsoft.EntityFrameworkCore;
using InventoryControl.Applications.Repositories;
using InventoryControl.Applications.Queries;
using InventoryControl.Applications.Outbox;
using InventoryControl.Applications.Reservations;
using InventoryControl.Applications.Receipts;

namespace InventoryControl.Infrastructure;

public static class ServiceCollectionExtensions
{
    public static IServiceCollection AddInfrastructureServices(this IServiceCollection services, IConfiguration configuration)
    {
        var connectionString = configuration.GetConnectionString("DefaultConnection")
            ?? throw new InvalidOperationException("ConnectionStrings:DefaultConnection is required.");
        services.AddDbContext<InventoryDbContext>(options => options.UseNpgsql(connectionString));
        services.AddScoped<InventoryItemDomainRepository>();
        services.AddScoped<IInventoryItemDomainRepository>(
            sp => sp.GetRequiredService<InventoryItemDomainRepository>());
        services.AddScoped<IInventoryItemQueryRepository>(
            sp => sp.GetRequiredService<InventoryItemDomainRepository>());
        services.AddScoped<IInventoryStockOutbox, PostgresInventoryStockOutbox>();
        services.AddScoped<IInventoryReservationOutbox, PostgresInventoryReservationRepository>();
        services.AddScoped<IInventoryGoodsReceiptStore, PostgresInventoryGoodsReceiptStore>();
        services.AddScoped<IIntegrationEventPublisher, IntegrationEventPublisher>();
        services.AddScoped<IDomainEventDispatcher, DomainEventDispatcher>();
        var outboxOptions = InventoryOutboxRelayOptions.FromConfiguration(configuration);
        services.AddSingleton(outboxOptions);
        if (outboxOptions.Enabled)
        {
            services.AddHostedService<InventoryIntegrationOutboxRelay>();
        }

        return services;
    }
}
