using SaleProducts.Applications.Queries;
using SaleProducts.Applications.UseCases;
using Microsoft.Extensions.DependencyInjection;

namespace SaleProducts.Applications;

/// <summary>
/// 提供 Product application layer 的 DI 註冊擴充方法。
/// </summary>
public static class ServiceCollectionExtensions
{
    /// <summary>
    /// 註冊 Product application layer 所需的 use case 與查詢服務。
    /// </summary>
    /// <param name="services">服務集合。</param>
    /// <returns>更新後的服務集合。</returns>
    public static IServiceCollection AddApplicationServices(this IServiceCollection services)
    {
        services.AddScoped<IProductQueryService, ProductQueryService>();
        services.AddScoped<ICreateProductUseCase, CreateProductUseCase>();
        services.AddScoped<IUpdateProductUseCase, UpdateProductUseCase>();
        services.AddScoped<IDeleteProductUseCase, DeleteProductUseCase>();
        services.AddScoped<IGetAllProductsUseCase, GetAllProductsUseCase>();
        services.AddScoped<IGetProductByIdUseCase, GetProductByIdUseCase>();
        return services;
    }
}
