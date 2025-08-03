using MediatR;
using SaleOrders.Domains;

namespace SaleOrders.Applications.Queries;

public record GetOrderByIdQuery(Guid Id) : IRequest<Order?>;

public class GetOrderByIdQueryHandler : IRequestHandler<GetOrderByIdQuery, Order?>
{
    private readonly IOrderRepository _orderRepository;

    public GetOrderByIdQueryHandler(IOrderRepository orderRepository)
    {
        this._orderRepository = orderRepository;
    }

    public async Task<Order?> Handle(GetOrderByIdQuery request, CancellationToken cancellationToken)
    {
        return await this._orderRepository.GetByIdAsync(request.Id, cancellationToken);
    }
}