using MediatR;
using SaleOrders.Applications.Dtos;
using SaleOrders.Applications.Repositories;

namespace SaleOrders.Applications.Queries;

public record GetOrderByIdQuery(Guid Id) : IRequest<OrderDto?>;

public class GetOrderByIdQueryHandler : IRequestHandler<GetOrderByIdQuery, OrderDto?>
{
    private readonly IOrderRepository _orderRepository;

    public GetOrderByIdQueryHandler(IOrderRepository orderRepository)
    {
        this._orderRepository = orderRepository;
    }

    public async Task<OrderDto?> Handle(GetOrderByIdQuery request, CancellationToken cancellationToken)
    {
        var byIdAsync = await this._orderRepository.GetByIdAsync(request.Id, cancellationToken);
        return byIdAsync == null ? null : new OrderDto(byIdAsync.Id, byIdAsync.OrderDate, byIdAsync.TotalAmount);
    }
}