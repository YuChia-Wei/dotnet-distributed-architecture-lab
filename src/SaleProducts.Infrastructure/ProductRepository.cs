using SaleProducts.Applications;
using SaleProducts.Domains;

namespace SaleProducts.Infrastructure;

public class ProductRepository : IProductRepository
{
    private readonly List<Product> _products = new();

    public Task<Product> GetByIdAsync(Guid id)
    {
        return Task.FromResult(this._products.FirstOrDefault(p => p.Id == id));
    }

    public Task AddAsync(Product product)
    {
        this._products.Add(product);
        return Task.CompletedTask;
    }

    public Task UpdateAsync(Product product)
    {
        var existingProduct = this._products.FirstOrDefault(p => p.Id == product.Id);
        if (existingProduct != null)
        {
            this._products.Remove(existingProduct);
            this._products.Add(product);
        }

        return Task.CompletedTask;
    }

    public Task DeleteAsync(Guid id)
    {
        var productToRemove = this._products.FirstOrDefault(p => p.Id == id);
        if (productToRemove != null)
        {
            this._products.Remove(productToRemove);
        }

        return Task.CompletedTask;
    }

    public Task<IEnumerable<Product>> GetAllAsync()
    {
        return Task.FromResult<IEnumerable<Product>>(this._products);
    }
}