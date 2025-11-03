using Lab.BuildingBlocks.Integrations;
using Lab.BoundedContextContracts.Orders.IntegrationEvents;
using SaleOrders.Applications.Repositories;
using SaleOrders.Domains;

namespace SaleOrders.Applications.Commands;

/// <summary>
/// 下單命令
/// </summary>
public record PlaceOrderCommand
{
    /// <summary>
    /// 下單命令
    /// </summary>
    /// <param name="OrderDate">訂單日期</param>
    /// <param name="TotalAmount">訂單總金額</param>
    /// <param name="productId"></param>
    /// <param name="ProductName"></param>
    /// <param name="Quantity"></param>
    public PlaceOrderCommand(DateTime OrderDate, decimal TotalAmount, Guid productId, string ProductName, int Quantity)
    {
        this.OrderDate = OrderDate;
        this.TotalAmount = TotalAmount;
        this.ProductName = ProductName;
        this.Quantity = Quantity;
        this.ProductId = productId;
    }

    public Guid ProductId { get; set; }

    /// <summary>訂單日期</summary>
    public DateTime OrderDate { get; init; }

    /// <summary>訂單總金額</summary>
    public decimal TotalAmount { get; init; }

    public string ProductName { get; init; }
    public int Quantity { get; init; }

    public void Deconstruct(out DateTime OrderDate, out decimal TotalAmount, out string ProductName, out int Quantity)
    {
        OrderDate = this.OrderDate;
        TotalAmount = this.TotalAmount;
        ProductName = this.ProductName;
        Quantity = this.Quantity;
    }
}

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
        var order = new Order(command.OrderDate, command.TotalAmount, command.ProductId, command.ProductName, command.Quantity);
        await repository.AddAsync(order);

        await publisher.PublishAsync(new OrderPlaced(order.Id, order.ProductId, order.ProductName, order.Quantity));

        return order.Id;
    }
}