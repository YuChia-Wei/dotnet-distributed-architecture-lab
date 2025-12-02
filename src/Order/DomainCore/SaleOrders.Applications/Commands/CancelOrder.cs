using Lab.BoundedContextContracts.Orders.IntegrationEvents;
using Lab.BuildingBlocks.Integrations;
using SaleOrders.Applications.Repositories;

namespace SaleOrders.Applications.Commands;

/// <summary>
/// 取消訂單命令
/// </summary>
public record CancelOrder(Guid OrderId);

/// <summary>
/// 取消訂單命令處理器
/// </summary>
public class CancelOrderHandler
{
    /// <summary>
    /// 處理取消訂單
    /// </summary>
    /// <param name="command">取消訂單命令</param>
    /// <param name="repository">訂單儲存庫</param>
    /// <param name="publisher">整合事件發布器</param>
    public static async Task HandleAsync(CancelOrder command, IOrderDomainRepository repository, IIntegrationEventPublisher publisher)
    {
        var order = await repository.GetByIdAsync(command.OrderId) ?? throw new KeyNotFoundException($"Order {command.OrderId} not found");

        order.Cancel();

        await repository.UpdateAsync(order);

        await publisher.PublishAsync(new OrderCancelled(order.Id));
    }
}