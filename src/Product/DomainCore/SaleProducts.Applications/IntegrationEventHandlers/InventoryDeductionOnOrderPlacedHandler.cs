using MediatR;
using Wolverine;
using Lab.MessageSchemas.Orders.IntegrationEvents;
using SaleProducts.Applications.Commands;

namespace SaleProducts.Applications.IntegrationEventHandlers;

public class InventoryDeductionOnOrderPlacedHandler : IMessageHandler<OrderPlaced>
{
    private readonly IMediator _mediator;

    public InventoryDeductionOnOrderPlacedHandler(IMediator mediator)
    {
        _mediator = mediator;
    }

    public async Task Handle(OrderPlaced integrationEvent)
    {
        var command = new CreateProductSaleCommand(
            integrationEvent.OrderId,
            integrationEvent.ProductName,
            integrationEvent.Quantity);

        await _mediator.Send(command);
    }
}
