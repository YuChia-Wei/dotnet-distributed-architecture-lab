using SaleProducts.Applications.Dtos;
using Lab.BuildingBlocks.Application;

namespace SaleProducts.Applications.Queries;

public interface IProductQueryRepository : IQueryRepository
{
    Task<IReadOnlyList<ProductDto>> GetAllAsync(CancellationToken cancellationToken);
    Task<ProductDto?> GetByIdAsync(Guid id, CancellationToken cancellationToken);
}
