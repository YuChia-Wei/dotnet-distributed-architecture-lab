using Lab.BuildingBlocks.Integrations;
using Lab.MessageSchemas.Orders.IntegrationEvents;
using SaleOrders.Applications.Repositories;
using SaleOrders.Domains;

namespace SaleOrders.Applications.Commands;

/// <summary>
/// 下單命令
/// </summary>
/// <param name="OrderDate">訂單日期</param>
/// <param name="TotalAmount">訂單總金額</param>
public record PlaceOrderCommand(DateTime OrderDate, decimal TotalAmount, string ProductName, int Quantity);

/// <summary>
/// 下單命令處理器
/// </summary>
public class PlaceOrderCommandHandler
{
    /// <summary>
    /// 處理命令
    /// </summary>
    /// <param name="command">下單命令</param>
    /// <param name="repository">訂單領域儲存庫</param>
    /// <param name="publisher"></param>
    /// <returns>新建訂單的識別碼</returns>
    public static async Task<Guid> HandleAsync(PlaceOrderCommand command, IOrderDomainRepository repository, IIntegrationEventPublisher publisher)
    {
        var order = new Order(command.OrderDate, command.TotalAmount, command.ProductName, command.Quantity);
        await repository.AddAsync(order);

        await publisher.PublishAsync(new OrderPlaced(order.Id, order.ProductName, order.Quantity));

        return order.Id;
    }
}