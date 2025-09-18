using Lab.MessageSchemas.Orders.IntegrationEvents;
using Microsoft.Extensions.Logging;
using SaleProducts.Applications.Commands;
using SaleProducts.Applications.Repositories;
using SaleProducts.Infrastructure.Clients;
using Wolverine;

namespace SaleProducts.Consumer.IntegrationEventHandlers;

/// <summary>
/// 處理訂單取消事件以補回商品庫存的整合事件處理常式。
/// </summary>
public static class OrderCancelledHandler
{
    /// <summary>
    /// 處理 <see cref="OrderCancelled"/> 事件並補回相關商品庫存。
    /// </summary>
    /// <param name="orderCancelled">訂單取消事件。</param>
    /// <param name="orderApiClient">訂單服務 API 用戶端。</param>
    /// <param name="messageBus">Wolverine 訊息匯流排。</param>
    /// <param name="historyRepository">事件處理歷程儲存庫。</param>
    /// <param name="logger">紀錄器。</param>
    public static async Task HandleAsync(
        OrderCancelled orderCancelled,
        IOrderApiClient orderApiClient,
        IMessageBus messageBus,
        IOrderCancellationHistoryRepository historyRepository,
        ILogger logger)
    {
        if (await historyRepository.HasProcessedAsync(orderCancelled.OrderId))
        {
            logger.LogInformation("訂單 {OrderId} 的取消事件已處理過，略過。", orderCancelled.OrderId);
            return;
        }

        var orderDetails = await orderApiClient.GetOrderDetailsAsync(orderCancelled.OrderId);
        foreach (var lineItem in orderDetails.LineItems)
        {
            if (lineItem.ProductId == Guid.Empty)
            {
                logger.LogWarning("訂單 {OrderId} 包含無效的商品識別碼，已略過。", orderCancelled.OrderId);
                continue;
            }

            if (lineItem.Quantity <= 0)
            {
                logger.LogWarning("訂單 {OrderId} 中商品 {ProductId} 的補貨數量 {Quantity} 無效，已略過。", orderCancelled.OrderId, lineItem.ProductId, lineItem.Quantity);
                continue;
            }

            var command = new RestockProductCommand(lineItem.ProductId, lineItem.Quantity);
            await messageBus.SendAsync(command);
        }

        await historyRepository.MarkProcessedAsync(orderCancelled.OrderId);
        logger.LogInformation("訂單 {OrderId} 的庫存補回流程完成。", orderCancelled.OrderId);
    }
}
