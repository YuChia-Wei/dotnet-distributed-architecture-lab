using Lab.BoundedContextContracts.Orders.IntegrationEvents;
using Lab.BuildingBlocks.Integrations;
using SaleOrders.Applications.Repositories;

namespace SaleOrders.Applications.UseCases;

/// <summary>
/// 交付訂單 use case 的輸入資料。
/// </summary>
public sealed class DeliverOrderInput
{
    /// <summary>
    /// 初始化交付訂單 use case 的輸入資料。
    /// </summary>
    /// <param name="orderId">訂單識別碼。</param>
    public DeliverOrderInput(Guid orderId)
    {
        this.OrderId = orderId;
    }

    /// <summary>
    /// 訂單識別碼。
    /// </summary>
    public Guid OrderId { get; }
}

/// <summary>
/// 定義交付訂單 use case 的入口。
/// </summary>
public interface IDeliverOrderUseCase
{
    /// <summary>
    /// 將指定訂單標記為已完成交付。
    /// </summary>
    /// <param name="input">交付訂單所需的輸入資料。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    Task ExecuteAsync(DeliverOrderInput input, CancellationToken cancellationToken = default);
}

/// <summary>
/// 交付訂單 use case 的預設實作。
/// </summary>
public class DeliverOrderUseCase(IOrderDomainRepository repository, IIntegrationEventPublisher publisher) : IDeliverOrderUseCase
{
    /// <summary>
    /// 執行交付訂單流程。
    /// </summary>
    /// <param name="input">交付訂單所需的輸入資料。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    public async Task ExecuteAsync(DeliverOrderInput input, CancellationToken cancellationToken = default)
    {
        var order = await repository.GetByIdAsync(input.OrderId, cancellationToken) ?? throw new KeyNotFoundException($"Order {input.OrderId} not found");

        order.Deliver();

        await repository.UpdateAsync(order, cancellationToken);

        await publisher.PublishAsync(new OrderDelivered(order.Id));
    }
}
