using Microsoft.Extensions.Logging;
using SaleOrders.Domains.DomainEvents;

namespace SaleOrders.Applications.DomainEventHandlers;

public class OrderPlacedEventHandler
{
    public static async Task HandleAsync(OrderPlacedDomainEvent domainDomainEvent, ILogger logger, CancellationToken cancellationToken)
    {
        logger.LogInformation("收到訂單的領域事件 {OrderId}：{Product} x{Qty}",
                               domainDomainEvent.OrderId, domainDomainEvent.ProductName, domainDomainEvent.Quantity);
    }
}