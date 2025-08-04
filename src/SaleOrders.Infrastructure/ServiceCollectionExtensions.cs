using System.Data;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Npgsql;
using SaleOrders.Applications.Repositories;
using SaleOrders.Infrastructure.Repositories;
using SaleOrders.Applications.IntegrationServices;
using SaleOrders.Infrastructure.IntegrationServices;

namespace SaleOrders.Infrastructure;

public static class ServiceCollectionExtensions
{
    public static IServiceCollection AddInfrastructureServices(this IServiceCollection services, IConfiguration configuration)
    {
        var connectionString = configuration.GetConnectionString("DefaultConnection");
        services.AddScoped<IDbConnection>(sp => new NpgsqlConnection(connectionString));
        services.AddScoped<IOrderDomainRepository, OrderDomainRepository>();
        services.AddScoped<IMessageQueuePublisher, MessageQueuePublisher>();
        return services;
    }
}