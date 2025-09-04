using SaleProducts.Domains;

namespace SaleProducts.Applications.Repositories;

public interface IProductRepository
{
    Task<Product?> GetByNameAsync(string name);
    Task UpdateAsync(Product product);
    Task AddAsync(Product product);
    Task<Product?> GetByIdAsync(Guid id);
    Task DeleteAsync(Guid id);
    Task<IEnumerable<Product>> ListAllAsync();
}
