using Lab.BoundedContextContracts.Orders.IntegrationEvents;
using SaleOrders.Applications.Repositories;

namespace SaleOrders.Applications.Commands;

/// <summary>
/// 訂單已完成交付命令
/// </summary>
public record DeliverOrder(Guid OrderId);

/// <summary>
/// 訂單已完成交付命令處理器
/// </summary>
public class DeliverOrderHandler
{
    /// <summary>
    /// 處理訂單已完成交付
    /// </summary>
    /// <param name="command">已完成交付命令</param>
    /// <param name="repository">訂單儲存庫</param>
    /// <param name="publisher">整合事件發布器</param>
    public static async Task HandleAsync(DeliverOrder command, IOrderDomainRepository repository, Lab.BuildingBlocks.Integrations.IIntegrationEventPublisher publisher)
    {
        var order = await repository.GetByIdAsync(command.OrderId) ?? throw new KeyNotFoundException($"Order {command.OrderId} not found");

        order.Deliver();

        await repository.UpdateAsync(order);

        await publisher.PublishAsync(new OrderDelivered(order.Id));
    }
}
