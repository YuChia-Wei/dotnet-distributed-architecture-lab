using SaleProducts.Applications.Dtos;
using SaleProducts.Applications.Repositories;

namespace SaleProducts.Applications.Queries;

public class ProductQueryHandler
{
    public static async Task<IEnumerable<ProductDto>> Handle(GetAllProductsQuery query, IProductDomainRepository repository)
    {
        var products = await repository.GetAllAsync();
        return products.Select(p => new ProductDto(p.Id, p.Name, p.Description, p.Price, p.Stock));
    }

    public static async Task<ProductDto> Handle(GetProductByIdQuery query, IProductDomainRepository repository)
    {
        var product = await repository.GetByIdAsync(query.Id);
        if (product == null)
        {
            throw new KeyNotFoundException($"Product with ID {query.Id} not found.");
        }

        return new ProductDto(product.Id, product.Name, product.Description, product.Price, product.Stock);
    }
}