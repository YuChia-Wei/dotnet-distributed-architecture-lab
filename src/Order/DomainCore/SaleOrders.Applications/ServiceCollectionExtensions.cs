using Microsoft.Extensions.DependencyInjection;
using SaleOrders.Applications.Queries;

namespace SaleOrders.Applications;

public static class ServiceCollectionExtensions
{
    public static IServiceCollection AddApplicationServices(this IServiceCollection services)
    {
        services.AddScoped<GetOrderDetailsQueryHandler>();
        return services;
    }
}
