using SaleOrders.Applications.Repositories;
using SaleOrders.Domains;

namespace SaleOrders.Applications.Commands;

public record CreateOrderCommand(DateTime OrderDate, decimal TotalAmount);

public class CreateOrderCommandHandler
{
    public static async Task<Guid> HandleAsync(CreateOrderCommand command, IOrderDomainRepository repository)
    {
        var order = new Order(command.OrderDate, command.TotalAmount);
        await repository.AddAsync(order);
        return order.Id;
    }
}