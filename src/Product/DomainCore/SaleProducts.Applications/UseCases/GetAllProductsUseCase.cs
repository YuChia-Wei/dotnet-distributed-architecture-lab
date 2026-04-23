using SaleProducts.Applications.Dtos;
using SaleProducts.Applications.Queries;

namespace SaleProducts.Applications.UseCases;

/// <summary>
/// 取得所有產品 use case 的輸入資料。
/// </summary>
public sealed class GetAllProductsInput
{
}

/// <summary>
/// 定義取得所有產品 use case 的入口。
/// </summary>
public interface IGetAllProductsUseCase
{
    /// <summary>
    /// 取得所有產品清單。
    /// </summary>
    /// <param name="input">查詢所有產品所需的輸入資料。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    /// <returns>產品 DTO 清單。</returns>
    Task<IReadOnlyList<ProductDto>> ExecuteAsync(GetAllProductsInput input, CancellationToken cancellationToken = default);
}

/// <summary>
/// 取得所有產品 use case 的預設實作。
/// </summary>
public sealed class GetAllProductsUseCase(IProductQueryService queryService) : IGetAllProductsUseCase
{
    /// <summary>
    /// 執行取得所有產品流程。
    /// </summary>
    /// <param name="input">查詢所有產品所需的輸入資料。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    /// <returns>產品 DTO 清單。</returns>
    public Task<IReadOnlyList<ProductDto>> ExecuteAsync(GetAllProductsInput input, CancellationToken cancellationToken = default)
        => queryService.GetAllAsync(cancellationToken);
}
