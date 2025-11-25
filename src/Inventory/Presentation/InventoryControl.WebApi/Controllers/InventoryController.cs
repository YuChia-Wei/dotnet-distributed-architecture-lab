using System;
using System.Threading.Tasks;
using InventoryControl.Applications.Commands;
using InventoryControl.Applications.Dtos;
using InventoryControl.Applications.Queries;
using InventoryControl.WebApi.Models.Requests;
using InventoryControl.WebApi.Models.Responses;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Wolverine;

namespace InventoryControl.WebApi.Controllers;

[ApiController]
[Route("api/[controller]")]
public class InventoryController : ControllerBase
{
    private readonly IMessageBus _bus;

    public InventoryController(IMessageBus bus)
    {
        this._bus = bus;
    }

    /// <summary>
    /// 扣庫
    /// </summary>
    /// <param name="productId">訂單識別碼。</param>
    /// <param name="request"></param>
    /// <returns>包含訂單行項目的結果。</returns>
    [HttpPost("product/{productId:guid}/decrease")]
    public async Task<IActionResult> DecreaseStock([FromRoute] Guid productId, [FromBody] DecreaseStockRequest request)
    {
        var resultDto = await this._bus.InvokeAsync<DecreaseStockResultDto>(new DecreaseStockCommand(productId, request.Stock));

        if (resultDto.IsSuccess)
        {
            var availableQuantityResponse = new AvailableQuantityResponse
            {
                ProductId = productId,
                AvailableQuantity = resultDto.CurrentStock
            };

            return this.Ok(availableQuantityResponse);
        }

        return this.BadRequest(resultDto.ErrorMessage);
    }

    /// <summary>
    /// 取得指定貨品的庫存數量
    /// </summary>
    /// <param name="productId">訂單識別碼。</param>
    /// <returns>包含訂單行項目的結果。</returns>
    [HttpGet("product/{productId:guid}")]
    [ProducesResponseType(typeof(AvailableQuantityResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> GetOrderDetails([FromRoute] Guid productId)
    {
        var resultDto = await this._bus.InvokeAsync<GetAvailableQuantityResultDto>(new GetInventoryItemAvailableQuantityQuery(productId));

        var availableQuantityResponse = new AvailableQuantityResponse
        {
            ProductId = resultDto.ProductId,
            AvailableQuantity = resultDto.AvailableStock
        };

        return this.Ok(availableQuantityResponse);
    }

    /// <summary>
    /// 進貨
    /// </summary>
    /// <param name="productId">訂單識別碼。</param>
    /// <param name="request"></param>
    /// <returns>包含訂單行項目的結果。</returns>
    [HttpPost("product/{productId:guid}/increase")]
    public async Task<IActionResult> IncreaseStock([FromRoute] Guid productId, [FromBody] IncreaseStockRequest request)
    {
        var resultDto = await this._bus.InvokeAsync<IncreaseStockResultDto>(new IncreaseStockCommand(productId, request.Stock));

        var availableQuantityResponse = new AvailableQuantityResponse
        {
            ProductId = productId,
            AvailableQuantity = resultDto.CurrentStock
        };

        return this.Ok(availableQuantityResponse);
    }

    /// <summary>
    /// 初始化商品庫存
    /// </summary>
    /// <param name="productId">訂單識別碼。</param>
    /// <param name="request"></param>
    /// <returns>包含訂單行項目的結果。</returns>
    [HttpPost("product/{productId:guid}")]
    public async Task<IActionResult> InitProductStock([FromRoute] Guid productId, [FromBody] InitProductStockRequest request)
    {
        var resultDto = await this._bus.InvokeAsync<InitProductStockResultDto>(new InitProductStockRequestCommand(productId, request.Stock));

        var availableQuantityResponse = new AvailableQuantityResponse
        {
            ProductId = productId,
            AvailableQuantity = resultDto.CurrentStock
        };

        return this.Ok(availableQuantityResponse);
    }

    /// <summary>
    /// 退貨回補庫存
    /// </summary>
    /// <param name="productId">訂單識別碼。</param>
    /// <param name="request"></param>
    /// <returns>包含訂單行項目的結果。</returns>
    [HttpPost("product/{productId:guid}/restock")]
    public async Task<IActionResult> Restock([FromRoute] Guid productId, [FromBody] ProductRestockRequest request)
    {
        var resultDto = await this._bus.InvokeAsync<RestockResultDto>(new RestockCommand(productId, request.Stock));

        var availableQuantityResponse = new AvailableQuantityResponse
        {
            ProductId = productId,
            AvailableQuantity = resultDto.CurrentStock
        };

        return this.Ok(availableQuantityResponse);
    }
}