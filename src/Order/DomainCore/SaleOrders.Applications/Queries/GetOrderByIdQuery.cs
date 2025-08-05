using SaleOrders.Applications.Dtos;
using SaleOrders.Applications.Repositories;

namespace SaleOrders.Applications.Queries;

public record GetOrderByIdQuery(Guid Id);

public class GetOrderByIdQueryHandler
{
    public static async Task<OrderDto> HandleAsync(GetOrderByIdQuery query, IOrderDomainRepository repository)
    {
        var order = await repository.GetByIdAsync(query.Id);
        if (order == null)
        {
            throw new KeyNotFoundException($"Order with ID {query.Id} not found.");
        }

        return new OrderDto(order.Id, order.OrderDate, order.TotalAmount);
    }
}