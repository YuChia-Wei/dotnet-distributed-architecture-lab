using Lab.BoundedContextContracts.Orders.DataTransferObjects;
using Lab.BuildingBlocks.Application;
using Microsoft.AspNetCore.Mvc;
using SaleOrders.Applications.UseCases;
using SaleOrders.WebApi.Models.Requests;

namespace SaleOrders.WebApi.Controllers;

/// <summary>
/// 提供訂單管理相關 HTTP 端點。
/// </summary>
[ApiController]
[Route("api/[controller]")]
public class OrdersController : ControllerBase
{

    /// <summary>
    /// 取消指定的訂單。
    /// </summary>
    /// <param name="orderId">訂單識別碼。</param>
    /// <param name="useCase">取消訂單 use case。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    [HttpPatch("{orderId:guid}/cancel")]
    [ProducesResponseType(204)]
    public async Task<IActionResult> CancelOrder(
        [FromRoute] Guid orderId,
        [FromServices] ICancelOrderUseCase useCase,
        CancellationToken cancellationToken)
    {
        await useCase.ExecuteAsync(new CancelOrderInput(orderId), cancellationToken);
        return this.NoContent();
    }

    /// <summary>
    /// 設定指定訂單為已出貨。
    /// </summary>
    /// <param name="orderId">訂單識別碼。</param>
    /// <param name="useCase">發貨訂單 use case。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    [HttpPatch("{orderId:guid}/ship")]
    [ProducesResponseType(204)]
    public async Task<IActionResult> ShipOrder(
        [FromRoute] Guid orderId,
        [FromServices] IShipOrderUseCase useCase,
        CancellationToken cancellationToken)
    {
        await useCase.ExecuteAsync(new ShipOrderInput(orderId), cancellationToken);
        return this.NoContent();
    }

    /// <summary>
    /// 設定指定訂單為已完成交付。
    /// </summary>
    /// <param name="orderId">訂單識別碼。</param>
    /// <param name="useCase">交付訂單 use case。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    [HttpPatch("{orderId:guid}/deliver")]
    [ProducesResponseType(204)]
    public async Task<IActionResult> DeliverOrder(
        [FromRoute] Guid orderId,
        [FromServices] IDeliverOrderUseCase useCase,
        CancellationToken cancellationToken)
    {
        await useCase.ExecuteAsync(new DeliverOrderInput(orderId), cancellationToken);
        return this.NoContent();
    }

    /// <summary>
    /// 建立新訂單。
    /// </summary>
    /// <param name="request">建立訂單的請求資料。</param>
    /// <param name="useCase">下單 use case。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    /// <returns>包含下單結果的 HTTP 回應。</returns>
    [HttpPost]
    [ProducesResponseType<Guid>(200)]
    public async Task<IActionResult> CreateOrder(
        [FromBody] PlaceOrderRequest request,
        [FromServices] IPlaceOrderUseCase useCase,
        CancellationToken cancellationToken)
    {
        Result<PlaceOrderOutput> placeOrderResult = await useCase.ExecuteAsync(
            new PlaceOrderInput(request.OrderDate, request.TotalAmount, request.ProductId, request.ProductName, request.Quantity),
            cancellationToken);

        if (!placeOrderResult.IsSuccess)
        {
            return this.BadRequest(placeOrderResult.ErrorMessage);
        }

        return this.Ok(placeOrderResult);
    }

    /// <summary>
    /// 取得訂單的詳細資訊。
    /// </summary>
    /// <param name="orderId">訂單識別碼。</param>
    /// <param name="useCase">取得訂單明細 use case。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    /// <returns>包含訂單行項目的結果。</returns>
    [HttpGet("{orderId:guid}")]
    [ProducesResponseType(typeof(OrderDetailsResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> GetOrderDetails(
        [FromRoute] Guid orderId,
        [FromServices] IGetOrderDetailsUseCase useCase,
        CancellationToken cancellationToken)
    {
        var orderDetails = await useCase.ExecuteAsync(new GetOrderDetailsInput(orderId), cancellationToken);
        if (orderDetails is null)
        {
            return this.NotFound();
        }

        return this.Ok(orderDetails);
    }
}
