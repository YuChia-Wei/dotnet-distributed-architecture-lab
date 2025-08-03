using SaleProducts.Domains;

namespace SaleProducts.Applications.Repositories;

public interface IProductRepository
{
    Task AddAsync(Product product);
    Task DeleteAsync(Guid id);
    Task<IEnumerable<Product>> GetAllAsync();
    Task<Product> GetByIdAsync(Guid id);
    Task UpdateAsync(Product product);
}