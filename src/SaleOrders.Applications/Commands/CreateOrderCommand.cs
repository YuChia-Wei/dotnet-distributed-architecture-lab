using MediatR;
using SaleOrders.Applications.Repositories;
using SaleOrders.Domains;

namespace SaleOrders.Applications.Commands;

public record CreateOrderCommand(DateTime OrderDate, decimal TotalAmount) : IRequest<Guid>;

public class CreateOrderCommandHandler : IRequestHandler<CreateOrderCommand, Guid>
{
    private readonly IOrderDomainRepository _orderDomainRepository;

    public CreateOrderCommandHandler(IOrderDomainRepository orderDomainRepository)
    {
        this._orderDomainRepository = orderDomainRepository;
    }

    public async Task<Guid> Handle(CreateOrderCommand command, CancellationToken cancellationToken)
    {
        var order = new Order(command.OrderDate, command.TotalAmount);

        await this._orderDomainRepository.AddAsync(order, cancellationToken);

        return order.Id;
    }
}