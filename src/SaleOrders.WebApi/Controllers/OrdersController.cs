using MediatR;
using Microsoft.AspNetCore.Mvc;
using SaleOrders.Applications.Commands;
using SaleOrders.Applications.Queries;

namespace SaleOrders.WebApi.Controllers;

[ApiController]
[Route("[controller]")]
public class OrdersController : ControllerBase
{
    private readonly IMediator _mediator;

    public OrdersController(IMediator mediator)
    {
        this._mediator = mediator;
    }

    [HttpPost]
    public async Task<IActionResult> CreateOrder([FromBody] CreateOrderCommand command)
    {
        var orderId = await this._mediator.Send(command);
        return this.CreatedAtAction(nameof(this.GetOrder), new
        {
            id = orderId
        }, null);
    }

    [HttpGet("{id}")]
    public async Task<IActionResult> GetOrder(Guid id)
    {
        var order = await this._mediator.Send(new GetOrderByIdQuery(id));
        return order is not null ? this.Ok(order) : this.NotFound();
    }
}