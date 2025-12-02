using Lab.BoundedContextContracts.Orders.IntegrationEvents;
using SaleOrders.Applications.Repositories;

namespace SaleOrders.Applications.Commands;

/// <summary>
/// 訂單商品已發貨命令
/// </summary>
public record ShipOrder(Guid OrderId);

/// <summary>
/// 訂單商品已發貨命令處理器
/// </summary>
public class ShipOrderHandler
{
    /// <summary>
    /// 處理訂單商品已發貨
    /// </summary>
    /// <param name="command">已發貨命令</param>
    /// <param name="repository">訂單儲存庫</param>
    /// <param name="publisher">整合事件發布器</param>
    public static async Task HandleAsync(ShipOrder command, IOrderDomainRepository repository, Lab.BuildingBlocks.Integrations.IIntegrationEventPublisher publisher)
    {
        var order = await repository.GetByIdAsync(command.OrderId) ?? throw new KeyNotFoundException($"Order {command.OrderId} not found");

        order.Ship();

        await repository.UpdateAsync(order);

        await publisher.PublishAsync(new OrderShipped(order.Id));
    }
}
