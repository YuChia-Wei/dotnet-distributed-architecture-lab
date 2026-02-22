using SaleProducts.Applications.Dtos;

namespace SaleProducts.Applications.Queries;

public interface IProductQueryRepository
{
    Task<IReadOnlyList<ProductDto>> GetAllAsync(CancellationToken cancellationToken = default);
    Task<ProductDto?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default);
}
