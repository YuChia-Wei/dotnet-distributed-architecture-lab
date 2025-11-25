using Lab.BoundedContextContracts.Inventory.Interactions;
using Lab.BoundedContextContracts.Orders.IntegrationEvents;
using Lab.BuildingBlocks.Integrations;
using SaleOrders.Applications.Gateways;
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
    /// <param name="inventoryGateway"></param>
    /// <param name="cancellationToken"></param>
    /// <returns>新建訂單的識別碼</returns>
    public static async Task<PlaceOrderResult> HandleAsync(
        PlaceOrderCommand command,
        IOrderDomainRepository repository,
        IIntegrationEventPublisher publisher,
        IInventoryGateway inventoryGateway,
        CancellationToken cancellationToken)
    {
        var order = new Order(command.OrderDate, command.TotalAmount, command.ProductId, command.ProductName, command.Quantity);

        var reserveInventoryResponseContract = await inventoryGateway.ReserveAsync(new ReserveInventoryRequestContract
        {
            ProductId = order.ProductId,
            Quantity = order.Quantity
        }, cancellationToken);

        if (!reserveInventoryResponseContract.Result)
        {
            return PlaceOrderResult.Fail("Inventory is not enough.");
        }

        await repository.AddAsync(order);

        await publisher.PublishAsync(new OrderPlaced(order.Id, order.ProductId, order.ProductName, order.Quantity));

        return PlaceOrderResult.Success(order.Id);
    }
}

public class PlaceOrderResult
{
    private PlaceOrderResult(bool isSuccess, Guid orderId, string? errorMessage = null)
    {
        this.IsSuccess = isSuccess;
        this.OrderId = orderId;
        this.ErrorMessage = errorMessage;
    }

    public bool IsSuccess { get; }
    public Guid OrderId { get; }
    public string? ErrorMessage { get; }

    public static PlaceOrderResult Fail(string errorMessage)
    {
        return new PlaceOrderResult(true, Guid.Empty, errorMessage);
    }

    public static PlaceOrderResult Success(Guid orderId)
    {
        return new PlaceOrderResult(true, orderId);
    }
}