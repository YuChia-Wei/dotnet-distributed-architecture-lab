using System.Data;
using SaleProducts.Applications.Repositories;
using SaleProducts.Domains;

namespace SaleProducts.Infrastructure.Repositories;

public class ProductDomainRepository : IProductDomainRepository
{
    private readonly IDbConnection _dbConnection;
    private readonly List<Product> _products = new();

    public ProductDomainRepository(IDbConnection dbConnection)
    {
        this._dbConnection = dbConnection;
    }

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