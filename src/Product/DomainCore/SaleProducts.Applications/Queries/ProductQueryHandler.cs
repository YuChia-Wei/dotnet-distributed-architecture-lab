using SaleProducts.Applications.Dtos;

namespace SaleProducts.Applications.Queries;

public class ProductQueryHandler
{
    public static async Task<IEnumerable<ProductDto>> Handle(GetAllProductsQuery query, IProductQueryService queryService)
    {
        return await queryService.GetAllAsync();
    }

    public static async Task<ProductDto> Handle(GetProductByIdQuery query, IProductQueryService queryService)
    {
        var product = await queryService.GetByIdAsync(query.Id);
        if (product == null)
        {
            throw new KeyNotFoundException($"Product with ID {query.Id} not found.");
        }

        return product;
    }
}
