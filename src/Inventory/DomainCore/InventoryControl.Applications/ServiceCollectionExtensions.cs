using InventoryControl.Applications.Queries;
using Microsoft.Extensions.DependencyInjection;

namespace InventoryControl.Applications;

public static class ServiceCollectionExtensions
{
    public static IServiceCollection AddApplicationServices(this IServiceCollection services)
    {
        return services;
    }
}
