using System.Data;
using Dapper;
using Lab.BuildingBlocks.Application;
using SaleProducts.Domains;
using SaleProducts.Domains.DomainEvents;

namespace SaleProducts.Infrastructure.Repositories;

public class ProductDomainRepository : IDomainRepository<Product, Guid>
{
    private readonly IDbConnection _dbConnection;

    public ProductDomainRepository(IDbConnection dbConnection)
    {
        this._dbConnection = dbConnection;
    }

    public async Task<Product?> FindByIdAsync(Guid id, CancellationToken cancellationToken = default)
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

    public async Task<IEnumerable<Product>> FindByIdsAsync(IEnumerable<Guid> ids, CancellationToken cancellationToken = default)
    {
        var idArray = ids.ToArray();
        if (idArray.Length == 0)
        {
            return Array.Empty<Product>();
        }

        const string productSql = """
                                  SELECT * FROM "products"
                                  WHERE "id" = ANY(@Ids) AND "isdeleted" = false
                                  """;
        var products = await this._dbConnection.QueryAsync<Product>(productSql, new
        {
            Ids = idArray
        });
        return products;
    }

    public async Task SaveAsync(Product product, CancellationToken cancellationToken = default)
    {
        if (this._dbConnection.State != ConnectionState.Open)
        {
            this._dbConnection.Open();
        }

        using var transaction = this._dbConnection.BeginTransaction();
        try
        {
            var isDelete = product.DomainEvents.Any(e => e is ProductDeleted);
            if (product.Version <= 0)
            {
                const string insertSql = """
                                         INSERT INTO "products" ("id", "name", "description", "price", "isdeleted", "version")
                                         VALUES (@Id, @Name, @Description, @Price, false, 1)
                                         """;
                await this._dbConnection.ExecuteAsync(insertSql, product, transaction);
            }
            else if (isDelete)
            {
                const string deleteSql = """
                                         UPDATE "products"
                                         SET "isdeleted" = true,
                                             "version" = "version" + 1
                                         WHERE "id" = @Id AND "version" = @Version AND "isdeleted" = false
                                         """;
                var affectedRows = await this._dbConnection.ExecuteAsync(deleteSql, product, transaction);
                if (affectedRows == 0)
                {
                    throw new DBConcurrencyException("The record has been modified by another user.");
                }
            }
            else
            {
                const string updateSql = """
                                         UPDATE "products"
                                         SET "name" = @Name,
                                             "description" = @Description,
                                             "price" = @Price,
                                             "version" = "version" + 1
                                         WHERE "id" = @Id AND "version" = @Version AND "isdeleted" = false
                                         """;
                var affectedRows = await this._dbConnection.ExecuteAsync(updateSql, product, transaction);
                if (affectedRows == 0)
                {
                    throw new DBConcurrencyException("The record has been modified by another user.");
                }

                const string deleteSalesSql = """DELETE FROM "productsales" WHERE "productid" = @ProductId""";
                await this._dbConnection.ExecuteAsync(deleteSalesSql, new
                {
                    ProductId = product.Id
                }, transaction);
            }

            transaction.Commit();
        }
        catch
        {
            transaction.Rollback();
            throw;
        }
    }

    public async Task SaveAllAsync(IEnumerable<Product> entities, CancellationToken cancellationToken = default)
    {
        foreach (var entity in entities)
        {
            await this.SaveAsync(entity, cancellationToken);
        }
    }

    public async Task DeleteAsync(Product entity, CancellationToken cancellationToken = default)
    {
        const string sql = """
                           UPDATE "products"
                           SET "isdeleted" = true,
                               "version" = "version" + 1
                           WHERE "id" = @Id AND "version" = @Version
                           """;
        var affectedRows = await this._dbConnection.ExecuteAsync(sql, new
        {
            entity.Id,
            entity.Version
        });
        if (affectedRows == 0)
        {
            throw new DBConcurrencyException("The record has been modified by another user.");
        }
    }
}
