using MediatR;
using SaleProducts.Applications.Dtos;
using SaleProducts.Applications.Repositories;

namespace SaleProducts.Applications.Queries;

public class QueryHandlers
    : IRequestHandler<GetAllProductsQuery, IEnumerable<ProductDto>>,
      IRequestHandler<GetProductByIdQuery, ProductDto>
{
    private readonly IProductRepository _productRepository;

    public QueryHandlers(IProductRepository productRepository)
    {
        this._productRepository = productRepository;
    }

    public async Task<IEnumerable<ProductDto>> Handle(GetAllProductsQuery query, CancellationToken cancellationToken)
    {
        var products = await this._productRepository.GetAllAsync();
        return products.Select(p => new ProductDto(p.Id, p.Name, p.Description, p.Price, p.Stock));
    }

    public async Task<ProductDto> Handle(GetProductByIdQuery query, CancellationToken cancellationToken)
    {
        var product = await this._productRepository.GetByIdAsync(query.Id);

        return new ProductDto(product.Id, product.Name, product.Description, product.Price, product.Stock);
    }
}