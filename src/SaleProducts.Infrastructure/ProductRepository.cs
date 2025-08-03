using SaleProducts.Applications;
using SaleProducts.Domains;

namespace SaleProducts.Infrastructure
{
    public class ProductRepository : IProductRepository
    {
        private readonly List<Product> _products = new();

        public Task<Product> GetByIdAsync(Guid id)
        {
            return Task.FromResult(_products.FirstOrDefault(p => p.Id == id));
        }

        public Task AddAsync(Product product)
        {
            _products.Add(product);
            return Task.CompletedTask;
        }

        public Task UpdateAsync(Product product)
        {
            var existingProduct = _products.FirstOrDefault(p => p.Id == product.Id);
            if (existingProduct != null)
            {
                _products.Remove(existingProduct);
                _products.Add(product);
            }
            return Task.CompletedTask;
        }

        public Task DeleteAsync(Guid id)
        {
            var productToRemove = _products.FirstOrDefault(p => p.Id == id);
            if (productToRemove != null)
            {
                _products.Remove(productToRemove);
            }
            return Task.CompletedTask;
        }

        public Task<IEnumerable<Product>> GetAllAsync()
        {
            return Task.FromResult<IEnumerable<Product>>(_products);
        }
    }
}