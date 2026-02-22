using SaleProducts.Applications.Dtos;
using Lab.BuildingBlocks.Application;
using SaleProducts.Domains;

namespace SaleProducts.Applications.Commands;

/// <summary>
/// 所有與產品有關的命令處理器
/// </summary>
public class ProductCommandsHandler
{
    public static async Task<ProductDto> HandleAsync(CreateProductCommand command, IDomainRepository<Product, Guid> repository)
    {
        var product = new Product(command.Name, command.Description, command.Price);
        await repository.SaveAsync(product);
        return new ProductDto(product.Id, product.Name, product.Description, product.Price);
    }

    public static async Task HandleAsync(UpdateProductCommand command, IDomainRepository<Product, Guid> repository)
    {
        var product = await repository.FindByIdAsync(command.Id);
        if (product == null)
        {
            throw new KeyNotFoundException($"Product with ID {command.Id} not found.");
        }

        product.Update(command.Name, command.Description, command.Price);
        await repository.SaveAsync(product);
    }

    public static async Task HandleAsync(DeleteProductCommand command, IDomainRepository<Product, Guid> repository)
    {
        var product = await repository.FindByIdAsync(command.Id);
        if (product == null)
        {
            throw new KeyNotFoundException($"Product with ID {command.Id} not found.");
        }

        product.Delete();
        await repository.SaveAsync(product);
    }
}
