using System.Data;
using Lab.BuildingBlocks.Domains;
using Lab.BuildingBlocks.Integrations;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Npgsql;
using SaleProducts.Applications.Repositories;
using SaleProducts.Infrastructure.BuildingBlocks;
using SaleProducts.Infrastructure.Repositories;

namespace SaleProducts.Infrastructure;

public static class ServiceCollectionExtensions
{
    public static IServiceCollection AddInfrastructureServices(this IServiceCollection services, IConfiguration configuration)
    {
        var connectionString = configuration.GetConnectionString("DefaultConnection");
        services.AddScoped<IDbConnection>(sp => new NpgsqlConnection(connectionString));
        services.AddScoped<IProductDomainRepository, ProductDomainRepository>();

        services.AddScoped<IDomainEventDispatcher, DomainEventDispatcher>();
        services.AddScoped<IIntegrationEventPublisher, IntegrationEventPublisher>();

        return services;
    }
}