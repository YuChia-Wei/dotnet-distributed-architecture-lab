
using SaleOrders.Applications.Commands;
using SaleOrders.Applications.Dtos;
using SaleOrders.Applications.Queries;
using SaleOrders.Applications.Repositories;
using SaleOrders.Domains;

namespace SaleOrders.Applications;

public class OrderHandlers
{
    public static async Task<Guid> Handle(CreateOrderCommand command, IOrderDomainRepository repository)
    {
        var order = new Order(command.OrderDate, command.TotalAmount);
        await repository.AddAsync(order);
        return order.Id;
    }

    public static async Task<OrderDto> Handle(GetOrderByIdQuery query, IOrderDomainRepository repository)
    {
        var order = await repository.GetByIdAsync(query.Id);
        if (order == null)
        {
            throw new KeyNotFoundException($"Order with ID {query.Id} not found.");
        }
        return new OrderDto(order.Id, order.OrderDate, order.TotalAmount);
    }
}
