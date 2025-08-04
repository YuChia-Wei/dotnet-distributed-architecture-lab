using SaleOrders.Applications.IntegrationServices;
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
/// 下單完成的 integration event
/// </summary>
/// <param name="OrderId">訂單的唯一識別碼</param>
/// <param name="ProductName">產品名稱</param>
/// <param name="Quantity">訂購數量</param>
public record OrderPlaced(Guid OrderId, string ProductName, int Quantity);

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
    public static async Task<Guid> HandleAsync(PlaceOrderCommand command, IOrderDomainRepository repository, IMessageQueuePublisher publisher)
    {
        var order = new Order(command.OrderDate, command.TotalAmount, command.ProductName, command.Quantity);
        await repository.AddAsync(order);

        await publisher.PublishAsync(new OrderPlaced(order.Id, order.ProductName, order.Quantity));

        return order.Id;
    }
}