using Microsoft.Extensions.DependencyInjection;
using SaleProducts.Applications;

namespace SaleProducts.Infrastructure
{
    public static class ServiceCollectionExtensions
    {
        public static IServiceCollection AddInfrastructureServices(this IServiceCollection services)
        {
            services.AddSingleton<IProductRepository, ProductRepository>(); // Using Singleton for in-memory repository
            return services;
        }
    }
}