using SaleProducts.Applications.Dtos;

namespace SaleProducts.Applications.Queries;

public class ProductQueryService : IProductQueryService
{
    private readonly IProductQueryRepository _repository;

    public ProductQueryService(IProductQueryRepository repository)
    {
        this._repository = repository;
    }

    public Task<IReadOnlyList<ProductDto>> GetAllAsync(CancellationToken cancellationToken = default)
        => this._repository.GetAllAsync(cancellationToken);

    public Task<ProductDto?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default)
        => this._repository.GetByIdAsync(id, cancellationToken);
}
