using System.Data;
using Lab.BuildingBlocks.Application;
using Lab.BuildingBlocks.Domains;
using Lab.BuildingBlocks.Integrations;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Npgsql;
using SaleOrders.Applications.Gateways;
using SaleOrders.Applications.Repositories;
using SaleOrders.Infrastructure.Applications.Repositories;
using SaleOrders.Infrastructure.BuildingBlocks;
using SaleOrders.Infrastructure.Gateways;

namespace SaleOrders.Infrastructure;

public static class ServiceCollectionExtensions
{
    public static IServiceCollection AddInfrastructureServices(this IServiceCollection services, IConfiguration configuration)
    {
        var connectionString = configuration.GetConnectionString("DefaultConnection");
        services.AddScoped<IDbConnection>(sp => new NpgsqlConnection(connectionString));
        // services.AddScoped<IOrderDomainRepository, OrderDomainRepository>();
        services.AddScoped<OrderEventSourcingRepository>();
        services.AddScoped<IOrderDomainRepository>(sp => sp.GetRequiredService<OrderEventSourcingRepository>());
        services.AddScoped<IOrderEventCommitter>(sp => sp.GetRequiredService<OrderEventSourcingRepository>());
        services.AddScoped<IntegrationEventPublisher>();
        services.AddScoped<IIntegrationEventPublisher>(sp => sp.GetRequiredService<IntegrationEventPublisher>());
        services.AddScoped<IDomainEventDispatcher, DomainEventDispatcher>();
        services.AddScoped<IInventoryGateway, InventoryGateway>();
        if (!string.IsNullOrWhiteSpace(connectionString))
        {
            services.AddHostedService<OrderIntegrationOutboxRelay>();
        }

        return services;
    }
}
