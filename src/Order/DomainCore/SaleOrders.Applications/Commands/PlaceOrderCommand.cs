using Lab.BoundedContextContracts.Inventory.Interactions;
using Lab.BoundedContextContracts.Orders.IntegrationEvents;
using Lab.BuildingBlocks.Application;
using Lab.BuildingBlocks.Integrations;
using SaleOrders.Applications.Gateways;
using SaleOrders.Applications.Repositories;
using SaleOrders.Domains;

namespace SaleOrders.Applications.UseCases;

/// <summary>
/// 下單 use case 的輸入資料。
/// </summary>
public sealed class PlaceOrderInput
{
    /// <summary>
    /// 初始化下單 use case 的輸入資料。
    /// </summary>
    /// <param name="orderDate">訂單日期。</param>
    /// <param name="totalAmount">訂單總金額。</param>
    /// <param name="productId">商品識別碼。</param>
    /// <param name="productName">商品名稱。</param>
    /// <param name="quantity">購買數量。</param>
    public PlaceOrderInput(DateTime orderDate, decimal totalAmount, Guid productId, string productName, int quantity)
    {
        this.OrderDate = orderDate;
        this.TotalAmount = totalAmount;
        this.ProductName = productName;
        this.Quantity = quantity;
        this.ProductId = productId;
    }

    /// <summary>
    /// 商品識別碼。
    /// </summary>
    public Guid ProductId { get; }

    /// <summary>
    /// 訂單日期。
    /// </summary>
    public DateTime OrderDate { get; }

    /// <summary>
    /// 訂單總金額。
    /// </summary>
    public decimal TotalAmount { get; }

    /// <summary>
    /// 商品名稱。
    /// </summary>
    public string ProductName { get; }

    /// <summary>
    /// 購買數量。
    /// </summary>
    public int Quantity { get; }
}

/// <summary>
/// 定義下單 use case 的入口。
/// </summary>
public interface IPlaceOrderUseCase
{
    /// <summary>
    /// 執行下單流程。
    /// </summary>
    /// <param name="input">下單所需的輸入資料。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    /// <returns>下單結果。</returns>
    Task<Result<PlaceOrderOutput>> ExecuteAsync(PlaceOrderInput input, CancellationToken cancellationToken = default);
}

/// <summary>
/// 下單 use case 的預設實作。
/// </summary>
public class PlaceOrderUseCase(
    IOrderDomainRepository repository,
    IIntegrationEventPublisher publisher,
    IInventoryGateway inventoryGateway) : IPlaceOrderUseCase
{
    /// <summary>
    /// 執行下單流程並建立訂單。
    /// </summary>
    /// <param name="input">下單所需的輸入資料。</param>
    /// <param name="repository">訂單領域儲存庫。</param>
    /// <param name="publisher">整合事件發布器。</param>
    /// <param name="inventoryGateway">庫存閘道。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    /// <returns>下單結果。</returns>
    public static async Task<Result<PlaceOrderOutput>> HandleAsync(
        PlaceOrderInput input,
        IOrderDomainRepository repository,
        IIntegrationEventPublisher publisher,
        IInventoryGateway inventoryGateway,
        CancellationToken cancellationToken)
    {
        var order = new Order(input.OrderDate, input.TotalAmount, input.ProductId, input.ProductName, input.Quantity);

        var reserveInventoryResponseContract = await inventoryGateway.ReserveAsync(new ReserveInventoryRequestContract
        {
            ProductId = order.ProductId,
            Quantity = order.Quantity
        }, cancellationToken);

        if (!reserveInventoryResponseContract.Result)
        {
            return Result<PlaceOrderOutput>.Failure("Inventory is not enough.");
        }

        await repository.AddAsync(order);

        await publisher.PublishAsync(new OrderPlaced(order.Id, order.ProductId, order.ProductName, order.Quantity));

        return Result<PlaceOrderOutput>.Success(new PlaceOrderOutput(order.Id));
    }

    /// <summary>
    /// 執行下單 use case。
    /// </summary>
    /// <param name="input">下單所需的輸入資料。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    /// <returns>下單結果。</returns>
    public Task<Result<PlaceOrderOutput>> ExecuteAsync(PlaceOrderInput input, CancellationToken cancellationToken = default)
    {
        return HandleAsync(input, repository, publisher, inventoryGateway, cancellationToken);
    }
}

/// <summary>
/// 下單 use case 的輸出資料。
/// </summary>
public sealed class PlaceOrderOutput
{
    /// <summary>
    /// 初始化下單輸出資料。
    /// </summary>
    /// <param name="orderId">訂單識別碼。</param>
    public PlaceOrderOutput(Guid orderId)
    {
        this.OrderId = orderId;
    }

    /// <summary>
    /// 取得建立完成的訂單識別碼。
    /// </summary>
    public Guid OrderId { get; }
}
