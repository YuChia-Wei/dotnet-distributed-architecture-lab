using System.Data;
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
        services.AddScoped<IOrderDomainRepository, OrderDomainRepository>();
        services.AddScoped<IIntegrationEventPublisher, IntegrationEventPublisher>();
        services.AddScoped<IDomainEventDispatcher, DomainEventDispatcher>();
        services.AddScoped<IInventoryGateway, InventoryGateway>();
        return services;
    }
}