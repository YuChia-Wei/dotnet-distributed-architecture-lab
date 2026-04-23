using Lab.BoundedContextContracts.Orders.DataTransferObjects;
using SaleOrders.Applications.Repositories;

namespace SaleOrders.Applications.UseCases;

/// <summary>
/// 取得訂單明細 use case 的輸入資料。
/// </summary>
public sealed class GetOrderDetailsInput
{
    /// <summary>
    /// 初始化取得訂單明細 use case 的輸入資料。
    /// </summary>
    /// <param name="orderId">訂單識別碼。</param>
    public GetOrderDetailsInput(Guid orderId)
    {
        this.OrderId = orderId;
    }

    /// <summary>
    /// 訂單識別碼。
    /// </summary>
    public Guid OrderId { get; }
}

/// <summary>
/// 定義取得訂單明細 use case 的入口。
/// </summary>
public interface IGetOrderDetailsUseCase
{
    /// <summary>
    /// 依訂單識別碼取得訂單明細。
    /// </summary>
    /// <param name="input">查詢訂單明細所需的輸入資料。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    /// <returns>訂單明細回應；若查無資料則為 <see langword="null"/>。</returns>
    Task<OrderDetailsResponse?> ExecuteAsync(GetOrderDetailsInput input, CancellationToken cancellationToken = default);
}

/// <summary>
/// 取得訂單明細 use case 的預設實作。
/// </summary>
public class GetOrderDetailsUseCase : IGetOrderDetailsUseCase
{
    private readonly IOrderDomainRepository _repository;

    /// <summary>
    /// 初始化取得訂單明細 use case。
    /// </summary>
    /// <param name="repository">訂單領域儲存庫。</param>
    public GetOrderDetailsUseCase(IOrderDomainRepository repository)
    {
        this._repository = repository;
    }

    /// <summary>
     /// 依訂單識別碼取得訂單明細。
    /// </summary>
    /// <param name="input">查詢參數。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    /// <returns>包含訂單品項的回應資料。</returns>
    public async Task<OrderDetailsResponse?> ExecuteAsync(GetOrderDetailsInput input, CancellationToken cancellationToken = default)
    {
        var order = await this._repository.GetByIdAsync(input.OrderId, cancellationToken);
        if (order is null)
        {
            return null;
        }

        var response = new OrderDetailsResponse
        {
            OrderId = order.Id,
            LineItems =
            [
                new LineItemDto
                {
                    ProductId = order.ProductId,
                    Quantity = order.Quantity
                }
            ]
        };

        return response;
    }
}
