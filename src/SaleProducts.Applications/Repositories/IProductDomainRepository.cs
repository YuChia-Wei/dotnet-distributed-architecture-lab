using SaleProducts.Domains;

namespace SaleProducts.Applications.Repositories;

public interface IProductDomainRepository
{
    Task AddAsync(Product product);
    Task DeleteAsync(Guid id);
    Task<IEnumerable<Product>> GetAllAsync();
    Task<Product> GetByIdAsync(Guid id);
    Task UpdateAsync(Product product);
}