using Microsoft.Extensions.Logging;
using SaleOrders.Domains.DomainEvents;

namespace SaleOrders.Applications.DomainEventHandlers;

public class OrderPlacedEventHandler
{
    public async Task Handle(OrderPlacedDomainEvent domainDomainEvent, ILogger _logger, CancellationToken cancellationToken)
    {
        _logger.LogInformation("收到訂單的領域事件 {OrderId}：{Product} x{Qty}",
                               domainDomainEvent.OrderId, domainDomainEvent.ProductName, domainDomainEvent.Quantity);
    }
}