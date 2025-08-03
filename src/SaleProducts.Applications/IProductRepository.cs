using SaleProducts.Domains;

namespace SaleProducts.Applications
{
    public interface IProductRepository
    {
        Task<Product> GetByIdAsync(Guid id);
        Task AddAsync(Product product);
        Task UpdateAsync(Product product);
        Task DeleteAsync(Guid id);
        Task<IEnumerable<Product>> GetAllAsync();
    }
}