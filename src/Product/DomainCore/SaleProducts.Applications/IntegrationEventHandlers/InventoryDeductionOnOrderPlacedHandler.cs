using Lab.MessageSchemas.Orders.IntegrationEvents;
using SaleProducts.Applications.Commands;

namespace SaleProducts.Applications.IntegrationEventHandlers;

public static class InventoryDeductionOnOrderPlacedHandler
{
    public static CreateProductSaleCommand Handle(OrderPlaced integrationEvent)
    {
        var command = new CreateProductSaleCommand(
            integrationEvent.OrderId,
            integrationEvent.ProductName,
            integrationEvent.Quantity);

        return command;
    }
}
