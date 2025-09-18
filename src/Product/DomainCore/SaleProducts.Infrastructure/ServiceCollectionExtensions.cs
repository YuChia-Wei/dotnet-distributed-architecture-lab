using System;
using System.Data;
using Lab.BuildingBlocks.Domains;
using Lab.BuildingBlocks.Integrations;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Npgsql;
using SaleProducts.Applications.Repositories;
using SaleProducts.Infrastructure.BuildingBlocks;
using SaleProducts.Infrastructure.Clients;
using SaleProducts.Infrastructure.Repositories;

namespace SaleProducts.Infrastructure;

public static class ServiceCollectionExtensions
{
    public static IServiceCollection AddInfrastructureServices(this IServiceCollection services, IConfiguration configuration)
    {
        var connectionString = configuration.GetConnectionString("DefaultConnection");
        services.AddScoped<IDbConnection>(sp => new NpgsqlConnection(connectionString));
        services.AddScoped<IProductDomainRepository, ProductDomainRepository>();
        services.AddScoped<IOrderCancellationHistoryRepository, OrderCancellationHistoryRepository>();

        services.AddScoped<IDomainEventDispatcher, DomainEventDispatcher>();
        services.AddScoped<IIntegrationEventPublisher, IntegrationEventPublisher>();

        var orderApiBaseAddress = configuration.GetValue<string>("Services:Orders:BaseAddress");
        if (string.IsNullOrWhiteSpace(orderApiBaseAddress))
        {
            orderApiBaseAddress = "http://orders-api:8080/";
        }

        services.AddHttpClient<IOrderApiClient, OrderApiClient>(client =>
        {
            client.BaseAddress = new Uri(orderApiBaseAddress);
        });

        return services;
    }
}
