using Lab.MessageSchemas.Orders.IntegrationEvents;
using Microsoft.Extensions.Logging;

namespace SaleProducts.Consumer.IntegrationEventHandlers;

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