using Microsoft.AspNetCore.Mvc;
using SaleProducts.Applications;
using SaleProducts.Applications.Commands;
using SaleProducts.Applications.Queries;

namespace SaleProducts.Api.Controllers;

/// <summary>
/// 產品管理 API
/// </summary>
[ApiController]
[Route("api/[controller]")]
public class ProductsController : ControllerBase
{
    private readonly ProductService _productService;

    public ProductsController(ProductService productService)
    {
        this._productService = productService;
    }

    /// <summary>
    /// 建立新產品
    /// </summary>
    /// <param name="command">建立產品的命令</param>
    /// <returns>建立的產品資訊</returns>
    [HttpPost]
    public async Task<IActionResult> CreateProduct([FromBody] CreateProductCommand command)
    {
        var productDto = await this._productService.Handle(command);
        return this.CreatedAtAction(nameof(this.GetProductById), new
        {
            id = productDto.Id
        }, productDto);
    }

    /// <summary>
    /// 刪除產品
    /// </summary>
    /// <param name="id">產品 ID</param>
    /// <returns>無內容</returns>
    [HttpDelete("{id}")]
    public async Task<IActionResult> DeleteProduct(Guid id)
    {
        try
        {
            await this._productService.Handle(new DeleteProductCommand(id));
            return this.NoContent();
        }
        catch (KeyNotFoundException ex)
        {
            return this.NotFound(ex.Message);
        }
    }

    /// <summary>
    /// 取得所有產品
    /// </summary>
    /// <returns>所有產品的列表</returns>
    [HttpGet]
    public async Task<IActionResult> GetAllProducts()
    {
        var products = await this._productService.Handle(new GetAllProductsQuery());
        return this.Ok(products);
    }

    /// <summary>
    /// 依 ID 取得產品
    /// </summary>
    /// <param name="id">產品 ID</param>
    /// <returns>產品資訊</returns>
    [HttpGet("{id}")]
    public async Task<IActionResult> GetProductById(Guid id)
    {
        var productDto = await this._productService.Handle(new GetProductByIdQuery(id));
        if (productDto == null)
        {
            return this.NotFound();
        }

        return this.Ok(productDto);
    }

    /// <summary>
    /// 更新產品資訊
    /// </summary>
    /// <param name="id">產品 ID</param>
    /// <param name="command">更新產品的命令</param>
    /// <returns>無內容</returns>
    [HttpPut("{id}")]
    public async Task<IActionResult> UpdateProduct(Guid id, [FromBody] UpdateProductCommand command)
    {
        if (id != command.Id)
        {
            return this.BadRequest("ID mismatch.");
        }

        try
        {
            await this._productService.Handle(command);
            return this.NoContent();
        }
        catch (KeyNotFoundException ex)
        {
            return this.NotFound(ex.Message);
        }
    }
}