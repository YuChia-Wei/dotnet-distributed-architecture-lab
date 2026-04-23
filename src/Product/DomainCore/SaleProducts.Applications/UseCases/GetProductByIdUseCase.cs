using SaleProducts.Applications.Dtos;
using SaleProducts.Applications.Queries;

namespace SaleProducts.Applications.UseCases;

/// <summary>
/// 依識別碼取得產品 use case 的輸入資料。
/// </summary>
public sealed class GetProductByIdInput
{
    /// <summary>
    /// 初始化依識別碼取得產品 use case 的輸入資料。
    /// </summary>
    /// <param name="id">產品識別碼。</param>
    public GetProductByIdInput(Guid id)
    {
        this.Id = id;
    }

    /// <summary>
    /// 產品識別碼。
    /// </summary>
    public Guid Id { get; }
}

/// <summary>
/// 定義依識別碼取得產品 use case 的入口。
/// </summary>
public interface IGetProductByIdUseCase
{
    /// <summary>
    /// 依產品識別碼取得產品資料。
    /// </summary>
    /// <param name="input">查詢產品所需的輸入資料。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    /// <returns>產品 DTO。</returns>
    Task<ProductDto> ExecuteAsync(GetProductByIdInput input, CancellationToken cancellationToken = default);
}

/// <summary>
/// 依識別碼取得產品 use case 的預設實作。
/// </summary>
public sealed class GetProductByIdUseCase(IProductQueryService queryService) : IGetProductByIdUseCase
{
    /// <summary>
    /// 執行依識別碼取得產品流程。
    /// </summary>
    /// <param name="input">查詢產品所需的輸入資料。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    /// <returns>產品 DTO。</returns>
    public async Task<ProductDto> ExecuteAsync(GetProductByIdInput input, CancellationToken cancellationToken = default)
    {
        var product = await queryService.GetByIdAsync(input.Id, cancellationToken);
        if (product == null)
        {
            throw new KeyNotFoundException($"Product with ID {input.Id} not found.");
        }

        return product;
    }
}
