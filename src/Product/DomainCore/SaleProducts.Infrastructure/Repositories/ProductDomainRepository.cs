using System.Data;
using Dapper;
using SaleProducts.Applications.Repositories;
using SaleProducts.Domains;

namespace SaleProducts.Infrastructure.Repositories;

public class ProductDomainRepository : IProductDomainRepository
{
    private readonly IDbConnection _dbConnection;

    public ProductDomainRepository(IDbConnection dbConnection)
    {
        _dbConnection = dbConnection;
    }

    public async Task<Product?> GetByIdAsync(Guid id)
    {
        const string sql = """
                           SELECT * FROM "Products"
                           WHERE "Id" = @Id AND "IsDeleted" = false
                           """;
        return await _dbConnection.QueryFirstOrDefaultAsync<Product>(sql, new { Id = id });
    }

    public async Task AddAsync(Product product)
    {
        const string sql = """
                           INSERT INTO "Products" ("Id", "Name", "Description", "Price", "Stock", "IsDeleted", "Version")
                           VALUES (@Id, @Name, @Description, @Price, @Stock, false, 1)
                           """;
        await _dbConnection.ExecuteAsync(sql, product);
    }

    public async Task UpdateAsync(Product product)
    {
        const string sql = """
                           UPDATE "Products"
                           SET "Name" = @Name,
                               "Description" = @Description,
                               "Price" = @Price,
                               "Stock" = @Stock,
                               "Version" = "Version" + 1
                           WHERE "Id" = @Id AND "Version" = @Version
                           """;
        var affectedRows = await _dbConnection.ExecuteAsync(sql, product);
        if (affectedRows == 0)
        {
            throw new DBConcurrencyException("The record has been modified by another user.");
        }
    }

    public async Task DeleteAsync(Guid id)
    {
        const string sql = """
                           UPDATE "Products"
                           SET "IsDeleted" = true,
                               "Version" = "Version" + 1
                           WHERE "Id" = @Id
                           """;
        await _dbConnection.ExecuteAsync(sql, new { Id = id });
    }

    public async Task<IEnumerable<Product>> GetAllAsync()
    {
        const string sql = """
                           SELECT * FROM "Products"
                           WHERE "IsDeleted" = false
                           """;
        return await _dbConnection.QueryAsync<Product>(sql);
    }
}