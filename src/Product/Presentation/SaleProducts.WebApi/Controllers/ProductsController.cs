using Microsoft.AspNetCore.Mvc;
using SaleProducts.Applications.Dtos;
using SaleProducts.Applications.UseCases;
using SaleProducts.WebApi.Models.Requests;
using SaleProducts.WebApi.Models.Responses;

namespace SaleProducts.WebApi.Controllers;

/// <summary>
/// 提供產品管理相關 HTTP 端點。
/// </summary>
[ApiController]
[Route("api/[controller]")]
public class ProductsController : ControllerBase
{
    /// <summary>
    /// 建立新產品。
    /// </summary>
    /// <param name="request">建立產品的請求</param>
    /// <param name="useCase">建立產品 use case。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    /// <returns>建立的產品資訊</returns>
    [HttpPost]
    public async Task<IActionResult> CreateProduct(
        [FromBody] CreateProductRequest request,
        [FromServices] ICreateProductUseCase useCase,
        CancellationToken cancellationToken)
    {
        var output = await useCase.ExecuteAsync(
            new CreateProductInput(request.Name, request.Description, request.Price),
            cancellationToken);
        var productResponse = new ProductResponse(output.Id, output.Name, output.Description, output.Price);
        return this.Ok(productResponse);
    }

    /// <summary>
    /// 刪除產品。
    /// </summary>
    /// <param name="id">產品 ID</param>
    /// <param name="useCase">刪除產品 use case。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    /// <returns>無內容</returns>
    [HttpDelete("{id:guid}")]
    public async Task<IActionResult> DeleteProduct(
        [FromRoute] Guid id,
        [FromServices] IDeleteProductUseCase useCase,
        CancellationToken cancellationToken)
    {
        await useCase.ExecuteAsync(new DeleteProductInput(id), cancellationToken);
        return this.Ok();
    }

    /// <summary>
    /// 取得所有產品。
    /// </summary>
    /// <param name="useCase">取得所有產品 use case。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    /// <returns>所有產品的列表</returns>
    [HttpGet]
    public async Task<IActionResult> GetAllProducts(
        [FromServices] IGetAllProductsUseCase useCase,
        CancellationToken cancellationToken)
    {
        IReadOnlyList<ProductDto> products = await useCase.ExecuteAsync(new GetAllProductsInput(), cancellationToken);
        var productResponses = products.Select(dto =>
                                                   new ProductResponse(dto.Id, dto.Name, dto.Description, dto.Price));

        return this.Ok(productResponses);
    }

    /// <summary>
    /// 依 ID 取得產品。
    /// </summary>
    /// <param name="id">產品 ID</param>
    /// <param name="useCase">取得單一產品 use case。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    /// <returns>產品資訊</returns>
    [HttpGet("{id:guid}")]
    public async Task<IActionResult> GetProductById(
        [FromRoute] Guid id,
        [FromServices] IGetProductByIdUseCase useCase,
        CancellationToken cancellationToken)
    {
        ProductDto productDto = await useCase.ExecuteAsync(new GetProductByIdInput(id), cancellationToken);

        return this.Ok(productDto);
    }

    /// <summary>
    /// 更新產品資訊。
    /// </summary>
    /// <param name="id">產品 ID</param>
    /// <param name="request">更新產品的請求</param>
    /// <param name="useCase">更新產品 use case。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    /// <returns>無內容</returns>
    [HttpPut("{id:guid}")]
    public async Task<IActionResult> UpdateProduct(
        [FromRoute] Guid id,
        [FromBody] UpdateProductRequest request,
        [FromServices] IUpdateProductUseCase useCase,
        CancellationToken cancellationToken)
    {
        await useCase.ExecuteAsync(
            new UpdateProductInput(id, request.Name, request.Description, request.Price),
            cancellationToken);
        return this.Ok();
    }
}
