using MediatR;
using SaleProducts.Applications.Dtos;
using SaleProducts.Applications.Repositories;

namespace SaleProducts.Applications.Queries;

public class QueryHandlers
    : IRequestHandler<GetAllProductsQuery, IEnumerable<ProductDto>>,
      IRequestHandler<GetProductByIdQuery, ProductDto>
{
    private readonly IProductDomainRepository _productDomainRepository;

    public QueryHandlers(IProductDomainRepository productDomainRepository)
    {
        this._productDomainRepository = productDomainRepository;
    }

    public async Task<IEnumerable<ProductDto>> Handle(GetAllProductsQuery query, CancellationToken cancellationToken)
    {
        var products = await this._productDomainRepository.GetAllAsync();
        return products.Select(p => new ProductDto(p.Id, p.Name, p.Description, p.Price, p.Stock));
    }

    public async Task<ProductDto> Handle(GetProductByIdQuery query, CancellationToken cancellationToken)
    {
        var product = await this._productDomainRepository.GetByIdAsync(query.Id);

        return new ProductDto(product.Id, product.Name, product.Description, product.Price, product.Stock);
    }
}