using MediatR;
using Microsoft.AspNetCore.Mvc;
using SaleProducts.Api.Models;
using SaleProducts.Api.Models.Requests;
using SaleProducts.Api.Models.Responses;
using SaleProducts.Applications.Commands;
using SaleProducts.Applications.Dtos;
using SaleProducts.Applications.Queries;

namespace SaleProducts.Api.Controllers;

/// <summary>
/// 產品管理 API
/// </summary>
[ApiController]
[Route("api/[controller]")]
public class ProductsController : ControllerBase
{
    private readonly IMediator _mediator;

    public ProductsController(IMediator mediator)
    {
        this._mediator = mediator;
    }

    /// <summary>
    /// 建立新產品
    /// </summary>
    /// <param name="request">建立產品的請求</param>
    /// <returns>建立的產品資訊</returns>
    [HttpPost]
    public async Task<IActionResult> CreateProduct([FromBody] CreateProductRequest request)
    {
        var command = new CreateProductCommand(request.Name, request.Description, request.Price, request.Stock);
        var dto = await this._mediator.Send(command);
        var productResponse = new ProductResponse(dto.Id, dto.Name, dto.Description, dto.Price, dto.Stock);
        return this.Ok(productResponse);
    }

    /// <summary>
    /// 刪除產品
    /// </summary>
    /// <param name="id">產品 ID</param>
    /// <returns>無內容</returns>
    [HttpDelete("{id:guid}")]
    public async Task<IActionResult> DeleteProduct([FromRoute] Guid id)
    {
        await this._mediator.Send(new DeleteProductCommand(id));
        return this.Ok();
    }

    /// <summary>
    /// 取得所有產品
    /// </summary>
    /// <returns>所有產品的列表</returns>
    [HttpGet]
    public async Task<IActionResult> GetAllProducts()
    {
        var getAllProductsQuery = new GetAllProductsQuery();
        var products = await this._mediator.Send<IEnumerable<ProductDto>>(getAllProductsQuery);
        var productResponses = products.Select(dto =>
                                                   new ProductResponse(dto.Id, dto.Name, dto.Description, dto.Price, dto.Stock));

        return this.Ok(productResponses);
    }

    /// <summary>
    /// 依 ID 取得產品
    /// </summary>
    /// <param name="id">產品 ID</param>
    /// <returns>產品資訊</returns>
    [HttpGet("{id:guid}")]
    public async Task<IActionResult> GetProductById([FromRoute] Guid id)
    {
        var productDto = await this._mediator.Send(new GetProductByIdQuery(id));

        return this.Ok(productDto);
    }

    /// <summary>
    /// 更新產品資訊
    /// </summary>
    /// <param name="id">產品 ID</param>
    /// <param name="request">更新產品的請求</param>
    /// <returns>無內容</returns>
    [HttpPut("{id:guid}")]
    public async Task<IActionResult> UpdateProduct([FromRoute] Guid id, [FromBody] UpdateProductRequest request)
    {
        var command = new UpdateProductCommand(id, request.Name, request.Description, request.Price, request.Stock);

        await this._mediator.Send(command);
        return this.Ok();
    }
}