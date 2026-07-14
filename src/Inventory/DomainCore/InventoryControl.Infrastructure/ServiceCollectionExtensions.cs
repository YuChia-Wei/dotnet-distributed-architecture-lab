using System.Data;
using InventoryControl.Infrastructure.Applications.Repositories;
using InventoryControl.Infrastructure.BuildingBlocks;
using Lab.BuildingBlocks.Application;
using Lab.BuildingBlocks.Domains;
using Lab.BuildingBlocks.Integrations;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Npgsql;
using InventoryControl.Applications.Repositories;
using InventoryControl.Applications.Queries;
using InventoryControl.Applications.Reservations;

namespace InventoryControl.Infrastructure;

public static class ServiceCollectionExtensions
{
    public static IServiceCollection AddInfrastructureServices(this IServiceCollection services, IConfiguration configuration)
    {
        var connectionString = configuration.GetConnectionString("DefaultConnection")
            ?? throw new InvalidOperationException("ConnectionStrings:DefaultConnection is required.");
        services.AddScoped<IDbConnection>(sp => new NpgsqlConnection(connectionString));
        services.AddScoped<InventoryItemDomainRepository>();
        services.AddScoped<IInventoryItemDomainRepository>(
            sp => sp.GetRequiredService<InventoryItemDomainRepository>());
        services.AddScoped<IInventoryItemQueryRepository>(
            sp => sp.GetRequiredService<InventoryItemDomainRepository>());
        services.AddScoped<IInventoryReservationRepository>(
            _ => new PostgresInventoryReservationRepository(connectionString));
        services.AddScoped<IIntegrationEventPublisher, IntegrationEventPublisher>();
        services.AddScoped<IDomainEventDispatcher, DomainEventDispatcher>();
        return services;
    }
}
