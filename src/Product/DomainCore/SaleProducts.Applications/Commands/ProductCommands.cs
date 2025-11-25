namespace SaleProducts.Applications.Commands;

public record DeleteProductCommand(Guid Id);

/// <summary>
/// 建立產品
/// </summary>
/// <param name="Name"></param>
/// <param name="Description"></param>
/// <param name="Price"></param>
public record CreateProductCommand(string Name, string Description, decimal Price);

/// <summary>
/// 更新產品資訊
/// </summary>
/// <param name="Id"></param>
/// <param name="Name"></param>
/// <param name="Description"></param>
/// <param name="Price"></param>
public record UpdateProductCommand(Guid Id, string Name, string Description, decimal Price);