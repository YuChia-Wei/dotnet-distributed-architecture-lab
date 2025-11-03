using Lab.BoundedContextContracts.Orders.DataTransferObjects;
using Microsoft.AspNetCore.Mvc;
using SaleOrders.Applications.Commands;
using SaleOrders.Applications.Queries;
using SaleOrders.WebApi.Models.Requests;
using Wolverine;

namespace SaleOrders.WebApi.Controllers;

[ApiController]
[Route("api/[controller]")]
public class OrdersController : ControllerBase
{
    private readonly IMessageBus _bus;

    public OrdersController(IMessageBus bus)
    {
        this._bus = bus;
    }

    /// <summary>
    /// 取消指定的訂單
    /// </summary>
    /// <param name="orderId">訂單識別碼</param>
    [HttpPatch("{orderId:guid}/cancel")]
    [ProducesResponseType(204)]
    public async Task<IActionResult> CancelOrder([FromRoute] Guid orderId)
    {
        await this._bus.InvokeAsync(new CancelOrder(orderId));
        return this.NoContent();
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
        var createOrderCommand =
            new PlaceOrderCommand(request.OrderDate, request.TotalAmount, request.ProductId, request.ProductName, request.Quantity);
        var orderId = await this._bus.InvokeAsync<Guid>(createOrderCommand);

        return this.Ok(orderId);
    }

    /// <summary>
    /// 取得訂單的詳細資訊。
    /// </summary>
    /// <param name="orderId">訂單識別碼。</param>
    /// <returns>包含訂單行項目的結果。</returns>
    [HttpGet("{orderId:guid}")]
    [ProducesResponseType(typeof(OrderDetailsResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> GetOrderDetails([FromRoute] Guid orderId)
    {
        var orderDetails = await this._bus.InvokeAsync<OrderDetailsResponse?>(new GetOrderDetailsQuery(orderId));
        if (orderDetails is null)
        {
            return this.NotFound();
        }

        return this.Ok(orderDetails);
    }
}