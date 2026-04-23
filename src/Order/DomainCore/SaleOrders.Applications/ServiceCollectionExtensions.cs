using Microsoft.Extensions.DependencyInjection;
using SaleOrders.Applications.UseCases;

namespace SaleOrders.Applications;

/// <summary>
/// 提供 Order application layer 的 DI 註冊擴充方法。
/// </summary>
public static class ServiceCollectionExtensions
{
    /// <summary>
    /// 註冊 Order application layer 所需的 use case。
    /// </summary>
    /// <param name="services">服務集合。</param>
    /// <returns>更新後的服務集合。</returns>
    public static IServiceCollection AddApplicationServices(this IServiceCollection services)
    {
        services.AddScoped<IPlaceOrderUseCase, PlaceOrderUseCase>();
        services.AddScoped<ICancelOrderUseCase, CancelOrderUseCase>();
        services.AddScoped<IShipOrderUseCase, ShipOrderUseCase>();
        services.AddScoped<IDeliverOrderUseCase, DeliverOrderUseCase>();
        services.AddScoped<IGetOrderDetailsUseCase, GetOrderDetailsUseCase>();
        return services;
    }
}
