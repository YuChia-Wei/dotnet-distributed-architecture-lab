using Microsoft.Extensions.DependencyInjection;
using SaleProducts.Applications.Commands;

namespace SaleProducts.Applications;

public static class ServiceCollectionExtensions
{
    public static IServiceCollection AddApplicationServices(this IServiceCollection services)
    {
        return services;
    }
}