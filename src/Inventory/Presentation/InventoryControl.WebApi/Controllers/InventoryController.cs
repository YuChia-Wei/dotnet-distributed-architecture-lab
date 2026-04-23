using System;
using System.Threading.Tasks;
using InventoryControl.Applications.UseCases;
using InventoryControl.WebApi.Models.Requests;
using InventoryControl.WebApi.Models.Responses;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;

namespace InventoryControl.WebApi.Controllers;

/// <summary>
/// 提供庫存管理相關 HTTP 端點。
/// </summary>
[ApiController]
[Route("api/[controller]")]
public class InventoryController : ControllerBase
{

    /// <summary>
    /// 扣除指定商品庫存。
    /// </summary>
    /// <param name="productId">商品識別碼。</param>
    /// <param name="request">扣庫請求資料。</param>
    /// <param name="useCase">扣除庫存 use case。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    /// <returns>包含可用庫存數量的結果。</returns>
    [HttpPost("product/{productId:guid}/decrease")]
    public async Task<IActionResult> DecreaseStock(
        [FromRoute] Guid productId,
        [FromBody] DecreaseStockRequest request,
        [FromServices] IDecreaseStockUseCase useCase,
        CancellationToken cancellationToken)
    {
        var resultDto = await useCase.ExecuteAsync(new DecreaseStockInput(productId, request.Stock), cancellationToken);

        if (resultDto.IsSuccess && resultDto.Value is not null)
        {
            var availableQuantityResponse = new AvailableQuantityResponse
            {
                ProductId = productId,
                AvailableQuantity = resultDto.Value.CurrentStock
            };

            return this.Ok(availableQuantityResponse);
        }

        return this.BadRequest(resultDto.ErrorMessage);
    }

    /// <summary>
    /// 取得指定商品的庫存數量。
    /// </summary>
    /// <param name="productId">商品識別碼。</param>
    /// <param name="useCase">取得可用庫存數量 use case。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    /// <returns>包含可用庫存數量的結果。</returns>
    [HttpGet("product/{productId:guid}")]
    [ProducesResponseType(typeof(AvailableQuantityResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> GetAvailableQuantity(
        [FromRoute] Guid productId,
        [FromServices] IGetInventoryItemAvailableQuantityUseCase useCase,
        CancellationToken cancellationToken)
    {
        var output = await useCase.ExecuteAsync(new GetInventoryItemAvailableQuantityInput(productId), cancellationToken);

        var availableQuantityResponse = new AvailableQuantityResponse
        {
            ProductId = output.ProductId,
            AvailableQuantity = output.AvailableStock
        };

        return this.Ok(availableQuantityResponse);
    }

    /// <summary>
    /// 增加指定商品庫存。
    /// </summary>
    /// <param name="productId">商品識別碼。</param>
    /// <param name="request">進貨請求資料。</param>
    /// <param name="useCase">增加庫存 use case。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    /// <returns>包含可用庫存數量的結果。</returns>
    [HttpPost("product/{productId:guid}/increase")]
    public async Task<IActionResult> IncreaseStock(
        [FromRoute] Guid productId,
        [FromBody] IncreaseStockRequest request,
        [FromServices] IIncreaseStockUseCase useCase,
        CancellationToken cancellationToken)
    {
        var resultDto = await useCase.ExecuteAsync(new IncreaseStockInput(productId, request.Stock), cancellationToken);

        if (!resultDto.IsSuccess || resultDto.Value is null)
        {
            return this.BadRequest(resultDto.ErrorMessage);
        }

        var availableQuantityResponse = new AvailableQuantityResponse
        {
            ProductId = productId,
            AvailableQuantity = resultDto.Value.CurrentStock
        };

        return this.Ok(availableQuantityResponse);
    }

    /// <summary>
    /// 初始化商品庫存。
    /// </summary>
    /// <param name="productId">商品識別碼。</param>
    /// <param name="request">初始化庫存請求資料。</param>
    /// <param name="useCase">初始化商品庫存 use case。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    /// <returns>包含可用庫存數量的結果。</returns>
    [HttpPost("product/{productId:guid}")]
    public async Task<IActionResult> InitProductStock(
        [FromRoute] Guid productId,
        [FromBody] InitProductStockRequest request,
        [FromServices] IInitProductStockUseCase useCase,
        CancellationToken cancellationToken)
    {
        var resultDto = await useCase.ExecuteAsync(new InitProductStockInput(productId, request.Stock), cancellationToken);

        if (!resultDto.IsSuccess || resultDto.Value is null)
        {
            return this.BadRequest(resultDto.ErrorMessage);
        }

        var availableQuantityResponse = new AvailableQuantityResponse
        {
            ProductId = productId,
            AvailableQuantity = resultDto.Value.CurrentStock
        };

        return this.Ok(availableQuantityResponse);
    }

    /// <summary>
    /// 退貨回補庫存。
    /// </summary>
    /// <param name="productId">商品識別碼。</param>
    /// <param name="request">退貨回補請求資料。</param>
    /// <param name="useCase">退貨回補 use case。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    /// <returns>包含可用庫存數量的結果。</returns>
    [HttpPost("product/{productId:guid}/restock")]
    public async Task<IActionResult> Restock(
        [FromRoute] Guid productId,
        [FromBody] ProductRestockRequest request,
        [FromServices] IRestockUseCase useCase,
        CancellationToken cancellationToken)
    {
        var resultDto = await useCase.ExecuteAsync(new RestockInput(productId, request.Stock), cancellationToken);

        if (!resultDto.IsSuccess || resultDto.Value is null)
        {
            return this.BadRequest(resultDto.ErrorMessage);
        }

        var availableQuantityResponse = new AvailableQuantityResponse
        {
            ProductId = productId,
            AvailableQuantity = resultDto.Value.CurrentStock
        };

        return this.Ok(availableQuantityResponse);
    }
}
