using System.Threading;
using Lab.MessageSchemas.Orders.DataTransferObjects;
using SaleOrders.Applications.Repositories;

namespace SaleOrders.Applications.Queries;

/// <summary>
/// 取得訂單明細的查詢。
/// </summary>
/// <param name="OrderId">訂單識別碼。</param>
public record GetOrderDetailsQuery(Guid OrderId);

/// <summary>
/// 負責處理 <see cref="GetOrderDetailsQuery"/> 的查詢處理常式。
/// </summary>
public class GetOrderDetailsQueryHandler
{
    private readonly IOrderDomainRepository _repository;

    /// <summary>
    /// 建立 <see cref="GetOrderDetailsQueryHandler"/>。
    /// </summary>
    /// <param name="repository">訂單領域儲存庫。</param>
    public GetOrderDetailsQueryHandler(IOrderDomainRepository repository)
    {
        this._repository = repository;
    }

    /// <summary>
    /// 依訂單識別碼取得訂單明細。
    /// </summary>
    /// <param name="query">查詢參數。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    /// <returns>包含訂單品項的回應資料。</returns>
    public async Task<OrderDetailsResponse?> Handle(GetOrderDetailsQuery query, CancellationToken cancellationToken = default)
    {
        var order = await this._repository.GetByIdAsync(query.OrderId, cancellationToken);
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
                    Quantity = order.Quantity,
                },
            ],
        };

        return response;
    }
}
