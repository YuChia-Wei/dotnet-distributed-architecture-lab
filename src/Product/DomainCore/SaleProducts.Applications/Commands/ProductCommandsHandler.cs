using SaleProducts.Applications.Dtos;
using SaleProducts.Applications.Repositories;
using SaleProducts.Domains;

namespace SaleProducts.Applications.Commands;

/// <summary>
/// 所有與產品有關的命令處理器
/// </summary>
public class ProductCommandsHandler
{
    public static async Task<ProductDto> HandleAsync(CreateProductCommand command, IProductDomainRepository repository)
    {
        var product = new Product(command.Name, command.Description, command.Price);
        await repository.AddAsync(product);
        return new ProductDto(product.Id, product.Name, product.Description, product.Price);
    }

    public static async Task HandleAsync(UpdateProductCommand command, IProductDomainRepository repository)
    {
        var product = await repository.GetByIdAsync(command.Id);
        if (product == null)
        {
            throw new KeyNotFoundException($"Product with ID {command.Id} not found.");
        }

        product.Update(command.Name, command.Description, command.Price);
        await repository.UpdateAsync(product);
    }

    public static async Task HandleAsync(DeleteProductCommand command, IProductDomainRepository repository)
    {
        var product = await repository.GetByIdAsync(command.Id);
        if (product == null)
        {
            throw new KeyNotFoundException($"Product with ID {command.Id} not found.");
        }

        await repository.DeleteAsync(command.Id);
    }
}