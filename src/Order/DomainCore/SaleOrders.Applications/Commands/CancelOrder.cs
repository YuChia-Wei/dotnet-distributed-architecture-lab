using Lab.BoundedContextContracts.Orders.IntegrationEvents;
using Lab.BuildingBlocks.Integrations;
using SaleOrders.Applications.Repositories;

namespace SaleOrders.Applications.UseCases;

/// <summary>
/// 取消訂單 use case 的輸入資料。
/// </summary>
public sealed class CancelOrderInput
{
    /// <summary>
    /// 初始化取消訂單 use case 的輸入資料。
    /// </summary>
    /// <param name="orderId">訂單識別碼。</param>
    public CancelOrderInput(Guid orderId)
    {
        this.OrderId = orderId;
    }

    /// <summary>
    /// 訂單識別碼。
    /// </summary>
    public Guid OrderId { get; }
}

/// <summary>
/// 定義取消訂單 use case 的入口。
/// </summary>
public interface ICancelOrderUseCase
{
    /// <summary>
    /// 取消指定訂單。
    /// </summary>
    /// <param name="input">取消訂單所需的輸入資料。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    Task ExecuteAsync(CancelOrderInput input, CancellationToken cancellationToken = default);
}

/// <summary>
/// 取消訂單 use case 的預設實作。
/// </summary>
public class CancelOrderUseCase(IOrderDomainRepository repository, IIntegrationEventPublisher publisher) : ICancelOrderUseCase
{
    /// <summary>
    /// 執行取消訂單流程。
    /// </summary>
    /// <param name="input">取消訂單所需的輸入資料。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    public async Task ExecuteAsync(CancelOrderInput input, CancellationToken cancellationToken = default)
    {
        var order = await repository.GetByIdAsync(input.OrderId, cancellationToken) ?? throw new KeyNotFoundException($"Order {input.OrderId} not found");

        order.Cancel();

        await repository.UpdateAsync(order, cancellationToken);

        await publisher.PublishAsync(new OrderCancelled(order.Id));
    }
}
