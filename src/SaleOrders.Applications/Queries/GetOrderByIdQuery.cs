using MediatR;
using SaleOrders.Applications.Dtos;
using SaleOrders.Applications.Repositories;

namespace SaleOrders.Applications.Queries;

public record GetOrderByIdQuery(Guid Id) : IRequest<OrderDto?>;

public class GetOrderByIdQueryHandler : IRequestHandler<GetOrderByIdQuery, OrderDto?>
{
    private readonly IOrderDomainRepository _orderDomainRepository;

    public GetOrderByIdQueryHandler(IOrderDomainRepository orderDomainRepository)
    {
        this._orderDomainRepository = orderDomainRepository;
    }

    public async Task<OrderDto?> Handle(GetOrderByIdQuery request, CancellationToken cancellationToken)
    {
        var byIdAsync = await this._orderDomainRepository.GetByIdAsync(request.Id, cancellationToken);
        return byIdAsync == null ? null : new OrderDto(byIdAsync.Id, byIdAsync.OrderDate, byIdAsync.TotalAmount);
    }
}