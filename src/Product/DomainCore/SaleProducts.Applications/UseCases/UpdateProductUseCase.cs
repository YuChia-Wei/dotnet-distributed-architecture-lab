using Lab.BuildingBlocks.Application;
using SaleProducts.Domains;

namespace SaleProducts.Applications.UseCases;

/// <summary>
/// 更新產品 use case 的輸入資料。
/// </summary>
public sealed class UpdateProductInput
{
    /// <summary>
    /// 初始化更新產品 use case 的輸入資料。
    /// </summary>
    /// <param name="id">產品識別碼。</param>
    /// <param name="name">產品名稱。</param>
    /// <param name="description">產品描述。</param>
    /// <param name="price">產品價格。</param>
    public UpdateProductInput(Guid id, string name, string description, decimal price)
    {
        this.Id = id;
        this.Name = name;
        this.Description = description;
        this.Price = price;
    }

    /// <summary>
    /// 產品識別碼。
    /// </summary>
    public Guid Id { get; }

    /// <summary>
    /// 產品名稱。
    /// </summary>
    public string Name { get; }

    /// <summary>
    /// 產品描述。
    /// </summary>
    public string Description { get; }

    /// <summary>
    /// 產品價格。
    /// </summary>
    public decimal Price { get; }
}

/// <summary>
/// 定義更新產品 use case 的入口。
/// </summary>
public interface IUpdateProductUseCase
{
    /// <summary>
    /// 更新既有產品資料。
    /// </summary>
    /// <param name="input">更新產品所需的輸入資料。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    Task ExecuteAsync(UpdateProductInput input, CancellationToken cancellationToken = default);
}

/// <summary>
/// 更新產品 use case 的預設實作。
/// </summary>
public sealed class UpdateProductUseCase(IDomainRepository<Product, Guid> repository) : IUpdateProductUseCase
{
    /// <summary>
    /// 執行更新產品流程。
    /// </summary>
    /// <param name="input">更新產品所需的輸入資料。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    public async Task ExecuteAsync(UpdateProductInput input, CancellationToken cancellationToken = default)
    {
        var product = await repository.FindByIdAsync(input.Id, cancellationToken);
        if (product == null)
        {
            throw new KeyNotFoundException($"Product with ID {input.Id} not found.");
        }

        product.Update(input.Name, input.Description, input.Price);
        await repository.SaveAsync(product, cancellationToken);
    }
}
