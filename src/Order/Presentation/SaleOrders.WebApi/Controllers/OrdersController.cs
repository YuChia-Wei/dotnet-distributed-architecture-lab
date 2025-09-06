using Microsoft.AspNetCore.Mvc;
using SaleOrders.Applications.Commands;
using SaleOrders.Applications.Queries;
using SaleOrders.WebApi.Models.Requests;
using SaleOrders.WebApi.Models.Responses;
using Wolverine;

namespace SaleOrders.WebApi.Controllers;

[ApiController]
[Route("[controller]")]
public class OrdersController : ControllerBase
{
    private readonly IMessageBus _bus;

    public OrdersController(IMessageBus bus)
    {
        this._bus = bus;
    }

    /// <summary>
    /// Handles the creation of a new order.
    /// </summary>
    /// <param name="request">An instance of <see cref="PlaceOrderCommand" /> containing order details such as date and total amount.</param>
    /// <returns>An <see cref="IActionResult" /> containing the unique identifier of the created order.</returns>
    [HttpPost]
    [ProducesResponseType<Guid>(200)]
    public async Task<IActionResult> CreateOrder([FromBody] PlaceOrderRequest request)
    {
        var createOrderCommand = new PlaceOrderCommand(request.OrderDate, request.TotalAmount,request.ProductId, request.ProductName, request.Quantity);
        var orderId = await this._bus.InvokeAsync<Guid>(createOrderCommand);

        return this.Ok(orderId);
    }

    /// <summary>
    /// Retrieves the details of an existing order by its unique identifier.
    /// </summary>
    /// <param name="id">The unique identifier of the order to retrieve.</param>
    /// <returns>An <see cref="IActionResult" /> containing the details of the requested order if found; otherwise, a not found response.</returns>
    [HttpGet("{id:guid}")]
    public async Task<IActionResult> GetOrder([FromRoute] Guid id)
    {
        var order = await this._bus.InvokeAsync<OrderResponse>(new GetOrderByIdQuery(id));
        if (order is null)
        {
            return this.NotFound();
        }

        var orderResponse = new OrderResponse(order.Id, order.OrderDate, order.TotalAmount);
        return this.Ok(orderResponse);
    }
}