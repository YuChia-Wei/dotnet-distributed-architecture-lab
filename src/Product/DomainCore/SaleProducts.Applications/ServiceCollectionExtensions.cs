using Microsoft.Extensions.DependencyInjection;

namespace SaleProducts.Applications;

public static class ServiceCollectionExtensions
{
    public static IServiceCollection AddApplicationServices(this IServiceCollection services)
    {
        return services;
    }
}