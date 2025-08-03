using MediatR;
using SaleOrders.Domains;

namespace SaleOrders.Applications.Commands;

public record CreateOrderCommand(DateTime OrderDate, decimal TotalAmount) : IRequest<Guid>;

public class CreateOrderCommandHandler : IRequestHandler<CreateOrderCommand, Guid>
{
    private readonly IOrderRepository _orderRepository;

    public CreateOrderCommandHandler(IOrderRepository orderRepository)
    {
        _orderRepository = orderRepository;
    }

    public async Task<Guid> Handle(CreateOrderCommand request, CancellationToken cancellationToken)
    {
        var order = new Order(); // In a real app, you'd use a factory or proper constructor
        typeof(Order).GetProperty(nameof(Order.Id))!.SetValue(order, Guid.NewGuid());
        typeof(Order).GetProperty(nameof(Order.OrderDate))!.SetValue(order, request.OrderDate);
        typeof(Order).GetProperty(nameof(Order.TotalAmount))!.SetValue(order, request.TotalAmount);

        await _orderRepository.AddAsync(order, cancellationToken);

        return order.Id;
    }
}
