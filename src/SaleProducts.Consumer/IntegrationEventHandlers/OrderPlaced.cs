using Microsoft.Extensions.Logging;
using Wolverine.Attributes;

namespace SaleProducts.Consumer.IntegrationEventHandlers;

/// <summary>
/// 收到訂單事件
/// </summary>
/// <param name="OrderId">訂單的唯一識別碼</param>
/// <param name="ProductName">產品名稱</param>
/// <param name="Quantity">訂購數量</param>
/// <remarks>
/// 因為還沒有利用獨立的專案打包跨 BC 的溝通合約物件 (application service event)，因此這邊需要明確定義要收的 msg id 是誰
/// </remarks>
[MessageIdentity("SaleOrders.Applications.Commands.OrderPlaced")]
public record OrderPlaced(Guid OrderId, string ProductName, int Quantity);

/// <summary>
/// 收到訂單後，要扣除庫存數量
/// </summary>
public static class InventoryDeductionOnOrderPlacedHandler
{
    // Wolverine 會自動掃描並注入 ILogger
    public static void HandleAsync(OrderPlaced @event, ILogger logger)
    {
        logger.LogInformation("收到訂單 {OrderId}：{Product} x{Qty}",
                              @event.OrderId, @event.ProductName, @event.Quantity);
    }
}