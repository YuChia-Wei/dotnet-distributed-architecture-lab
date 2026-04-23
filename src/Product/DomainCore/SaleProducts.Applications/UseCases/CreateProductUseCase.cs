using Lab.BuildingBlocks.Application;
using SaleProducts.Domains;

namespace SaleProducts.Applications.UseCases;

/// <summary>
/// 建立產品 use case 的輸入資料。
/// </summary>
public sealed class CreateProductInput
{
    /// <summary>
    /// 初始化建立產品 use case 的輸入資料。
    /// </summary>
    /// <param name="name">產品名稱。</param>
    /// <param name="description">產品描述。</param>
    /// <param name="price">產品價格。</param>
    public CreateProductInput(string name, string description, decimal price)
    {
        this.Name = name;
        this.Description = description;
        this.Price = price;
    }

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
/// 建立產品 use case 的輸出資料。
/// </summary>
public sealed class CreateProductOutput
{
    /// <summary>
    /// 初始化建立產品 use case 的輸出資料。
    /// </summary>
    /// <param name="id">產品識別碼。</param>
    /// <param name="name">產品名稱。</param>
    /// <param name="description">產品描述。</param>
    /// <param name="price">產品價格。</param>
    public CreateProductOutput(Guid id, string name, string description, decimal price)
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
/// 定義建立產品 use case 的入口。
/// </summary>
public interface ICreateProductUseCase
{
    /// <summary>
    /// 建立新的產品。
    /// </summary>
    /// <param name="input">建立產品所需的輸入資料。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    /// <returns>建立完成後的產品資料。</returns>
    Task<CreateProductOutput> ExecuteAsync(CreateProductInput input, CancellationToken cancellationToken = default);
}

/// <summary>
/// 建立產品 use case 的預設實作。
/// </summary>
public sealed class CreateProductUseCase(IDomainRepository<Product, Guid> repository) : ICreateProductUseCase
{
    /// <summary>
    /// 執行建立產品流程。
    /// </summary>
    /// <param name="input">建立產品所需的輸入資料。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    /// <returns>建立完成後的產品資料。</returns>
    public async Task<CreateProductOutput> ExecuteAsync(CreateProductInput input, CancellationToken cancellationToken = default)
    {
        var product = new Product(input.Name, input.Description, input.Price);
        await repository.SaveAsync(product, cancellationToken);
        return new CreateProductOutput(product.Id, product.Name, product.Description, product.Price);
    }
}
