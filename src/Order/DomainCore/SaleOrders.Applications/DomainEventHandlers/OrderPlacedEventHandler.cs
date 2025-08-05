using Lab.BuildingBlocks.Integrations;
using Lab.MessageSchemas.Orders.IntegrationEvents;
using SaleOrders.Domains.DomainEvents;

namespace SaleOrders.Applications.DomainEventHandlers;

public class OrderPlacedEventHandler
{
    private readonly IIntegrationEventPublisher _publisher;

    public OrderPlacedEventHandler(IIntegrationEventPublisher publisher)
    {
        this._publisher = publisher;
    }

    public async Task Handle(OrderPlacedEvent domainEvent, CancellationToken cancellationToken)
    {
        // 轉發為整合事件
        await this._publisher.PublishAsync(new OrderPlaced(domainEvent.OrderId, domainEvent.ProductName, domainEvent.Quantity));
    }
}