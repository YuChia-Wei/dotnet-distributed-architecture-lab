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
        this._dbConnection = dbConnection;
    }

    public async Task<Product?> GetByIdAsync(Guid id)
    {
        const string productSql = """
                                  SELECT * FROM "products"
                                  WHERE "id" = @Id AND "isdeleted" = false
                                  """;
        var product = await this._dbConnection.QueryFirstOrDefaultAsync<Product>(productSql, new
        {
            Id = id
        });

        return product;
    }

    public async Task AddAsync(Product product)
    {
        if (this._dbConnection.State != ConnectionState.Open)
        {
            this._dbConnection.Open();
        }

        using var transaction = this._dbConnection.BeginTransaction();

        try
        {
            const string productSql = """
                                      INSERT INTO "products" ("id", "name", "description", "price", "isdeleted", "version")
                                      VALUES (@Id, @Name, @Description, @Price, false, 1)
                                      """;
            await this._dbConnection.ExecuteAsync(productSql, product, transaction);

            transaction.Commit();
        }
        catch
        {
            transaction.Rollback();
            throw;
        }
    }

    public async Task UpdateAsync(Product product)
    {
        if (this._dbConnection.State != ConnectionState.Open)
        {
            this._dbConnection.Open();
        }

        using var transaction = this._dbConnection.BeginTransaction();
        try
        {
            const string productSql = """
                                      UPDATE "products"
                                      SET "name" = @Name,
                                          "description" = @Description,
                                          "price" = @Price,
                                          "version" = "version" + 1
                                      WHERE "id" = @Id AND "version" = @Version
                                      """;
            var affectedRows = await this._dbConnection.ExecuteAsync(productSql, product, transaction);
            if (affectedRows == 0)
            {
                throw new DBConcurrencyException("The record has been modified by another user.");
            }

            const string deleteSalesSql = """DELETE FROM "productsales" WHERE "productid" = @ProductId""";
            await this._dbConnection.ExecuteAsync(deleteSalesSql, new
            {
                ProductId = product.Id
            }, transaction);

            transaction.Commit();
        }
        catch
        {
            transaction.Rollback();
            throw;
        }
    }

    public async Task DeleteAsync(Guid id)
    {
        const string sql = """
                           UPDATE "products"
                           SET "isdeleted" = true,
                               "version" = "version" + 1
                           WHERE "id" = @Id
                           """;
        await this._dbConnection.ExecuteAsync(sql, new
        {
            Id = id
        });
    }

    public async Task<IEnumerable<Product>> GetAllAsync()
    {
        const string sql = """
                           SELECT p.*
                           FROM "products" AS p
                           WHERE p."isdeleted" = false
                           """;

        return await this._dbConnection.QueryAsync<Product>(sql);
    }
}