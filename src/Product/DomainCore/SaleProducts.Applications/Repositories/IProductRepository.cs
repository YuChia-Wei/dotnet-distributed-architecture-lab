using SaleProducts.Domains;

namespace SaleProducts.Applications.Repositories;

public interface IProductRepository
{
    Task AddAsync(Product product);
    Task DeleteAsync(Guid id);
    Task<Product?> GetByIdAsync(Guid id);
    Task<Product?> GetByNameAsync(string name);
    Task<IEnumerable<Product>> ListAllAsync();
    Task UpdateAsync(Product product);
}