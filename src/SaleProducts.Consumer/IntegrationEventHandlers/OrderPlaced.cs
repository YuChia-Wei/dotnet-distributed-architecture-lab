using Microsoft.Extensions.Logging;

namespace SaleProducts.Consumer.IntegrationEventHandlers;

/// <summary>
/// 收到訂單事件
/// </summary>
/// <param name="OrderId">訂單的唯一識別碼</param>
/// <param name="ProductName">產品名稱</param>
/// <param name="Quantity">訂購數量</param>
public record OrderPlaced(Guid OrderId, string ProductName, int Quantity);

/// <summary>
/// 收到訂單後，要扣除庫存數量
/// </summary>
public static class InventoryDeductionOnOrderPlaced
{
    // Wolverine 會自動掃描並注入 ILogger
    public static void Handle(OrderPlaced @event, ILogger logger)
    {
        logger.LogInformation("收到訂單 {OrderId}：{Product} x{Qty}",
                              @event.OrderId, @event.ProductName, @event.Quantity);
    }
}