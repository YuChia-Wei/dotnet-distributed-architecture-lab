using InventoryControl.Applications.UseCases;
using Microsoft.Extensions.DependencyInjection;

namespace InventoryControl.Applications;

/// <summary>
/// 提供 Inventory application layer 的 DI 註冊擴充方法。
/// </summary>
public static class ServiceCollectionExtensions
{
    /// <summary>
    /// 註冊 Inventory application layer 所需的 use case。
    /// </summary>
    /// <param name="services">服務集合。</param>
    /// <returns>更新後的服務集合。</returns>
    public static IServiceCollection AddApplicationServices(this IServiceCollection services)
    {
        services.AddScoped<IDecreaseStockUseCase, DecreaseStockUseCase>();
        services.AddScoped<IIncreaseStockUseCase, IncreaseStockUseCase>();
        services.AddScoped<IInitProductStockUseCase, InitProductStockUseCase>();
        services.AddScoped<IRestockUseCase, RestockUseCase>();
        services.AddScoped<IGetInventoryItemAvailableQuantityUseCase, GetInventoryItemAvailableQuantityUseCase>();
        return services;
    }
}
