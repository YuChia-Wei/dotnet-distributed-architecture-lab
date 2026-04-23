using Lab.BuildingBlocks.Application;
using SaleProducts.Domains;

namespace SaleProducts.Applications.UseCases;

/// <summary>
/// 刪除產品 use case 的輸入資料。
/// </summary>
public sealed class DeleteProductInput
{
    /// <summary>
    /// 初始化刪除產品 use case 的輸入資料。
    /// </summary>
    /// <param name="id">產品識別碼。</param>
    public DeleteProductInput(Guid id)
    {
        this.Id = id;
    }

    /// <summary>
    /// 產品識別碼。
    /// </summary>
    public Guid Id { get; }
}

/// <summary>
/// 定義刪除產品 use case 的入口。
/// </summary>
public interface IDeleteProductUseCase
{
    /// <summary>
    /// 刪除指定產品。
    /// </summary>
    /// <param name="input">刪除產品所需的輸入資料。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    Task ExecuteAsync(DeleteProductInput input, CancellationToken cancellationToken = default);
}

/// <summary>
/// 刪除產品 use case 的預設實作。
/// </summary>
public sealed class DeleteProductUseCase(IDomainRepository<Product, Guid> repository) : IDeleteProductUseCase
{
    /// <summary>
    /// 執行刪除產品流程。
    /// </summary>
    /// <param name="input">刪除產品所需的輸入資料。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    public async Task ExecuteAsync(DeleteProductInput input, CancellationToken cancellationToken = default)
    {
        var product = await repository.FindByIdAsync(input.Id, cancellationToken);
        if (product == null)
        {
            throw new KeyNotFoundException($"Product with ID {input.Id} not found.");
        }

        product.Delete();
        await repository.SaveAsync(product, cancellationToken);
    }
}
