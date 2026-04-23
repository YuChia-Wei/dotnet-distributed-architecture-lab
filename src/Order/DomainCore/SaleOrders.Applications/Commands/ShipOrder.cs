using Lab.BoundedContextContracts.Orders.IntegrationEvents;
using Lab.BuildingBlocks.Integrations;
using SaleOrders.Applications.Repositories;

namespace SaleOrders.Applications.UseCases;

/// <summary>
/// 發貨訂單 use case 的輸入資料。
/// </summary>
public sealed class ShipOrderInput
{
    /// <summary>
    /// 初始化發貨訂單 use case 的輸入資料。
    /// </summary>
    /// <param name="orderId">訂單識別碼。</param>
    public ShipOrderInput(Guid orderId)
    {
        this.OrderId = orderId;
    }

    /// <summary>
    /// 訂單識別碼。
    /// </summary>
    public Guid OrderId { get; }
}

/// <summary>
/// 定義發貨訂單 use case 的入口。
/// </summary>
public interface IShipOrderUseCase
{
    /// <summary>
    /// 將指定訂單標記為已發貨。
    /// </summary>
    /// <param name="input">發貨訂單所需的輸入資料。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    Task ExecuteAsync(ShipOrderInput input, CancellationToken cancellationToken = default);
}

/// <summary>
/// 發貨訂單 use case 的預設實作。
/// </summary>
public class ShipOrderUseCase(IOrderDomainRepository repository, IIntegrationEventPublisher publisher) : IShipOrderUseCase
{
    /// <summary>
    /// 執行發貨訂單流程。
    /// </summary>
    /// <param name="input">發貨訂單所需的輸入資料。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    public async Task ExecuteAsync(ShipOrderInput input, CancellationToken cancellationToken = default)
    {
        var order = await repository.GetByIdAsync(input.OrderId, cancellationToken) ?? throw new KeyNotFoundException($"Order {input.OrderId} not found");

        order.Ship();

        await repository.UpdateAsync(order, cancellationToken);

        await publisher.PublishAsync(new OrderShipped(order.Id));
    }
}
