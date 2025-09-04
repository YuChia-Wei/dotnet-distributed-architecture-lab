using Lab.MessageSchemas.Orders.IntegrationEvents;
using Microsoft.Extensions.Logging;
using SaleProducts.Applications.Commands;
using Wolverine;

namespace SaleProducts.Consumer.IntegrationEventHandlers;

/// <summary>
/// 收到訂單後，要扣除庫存數量
/// </summary>
public static class InventoryDeductionOnOrderPlacedHandler
{
    // Wolverine 會自動掃描並注入 ILogger
    public static async Task HandleAsync(OrderPlaced @event, ILogger logger, IMessageBus messageBus)
    {
        logger.LogInformation("收到訂單 {OrderId}：{Product} x{Qty}",
                              @event.OrderId, @event.ProductName, @event.Quantity);
        var productSaleCommand = new CreateProductSaleCommand(@event.OrderId, @event.ProductName, @event.Quantity);
        await messageBus.SendAsync(productSaleCommand);
    }
}