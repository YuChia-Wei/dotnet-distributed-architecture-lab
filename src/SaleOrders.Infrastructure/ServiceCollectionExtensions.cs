using System.Data;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Npgsql;
using SaleOrders.Applications.Repositories;
using SaleOrders.Infrastructure.Repositories;

namespace SaleOrders.Infrastructure;

public static class ServiceCollectionExtensions
{
    public static IServiceCollection AddInfrastructureServices(this IServiceCollection services, IConfiguration configuration)
    {
        var connectionString = configuration.GetConnectionString("DefaultConnection");
        services.AddScoped<IDbConnection>(sp => new NpgsqlConnection(connectionString));
        services.AddScoped<IOrderDomainRepository, OrderDomainRepository>();
        return services;
    }
}