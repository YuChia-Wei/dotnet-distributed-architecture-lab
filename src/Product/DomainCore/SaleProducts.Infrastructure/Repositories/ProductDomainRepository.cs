using System.Data;
using System.Reflection;
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

        if (product is not null)
        {
            await this.LoadSalesAsync(product);
        }

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
                                      INSERT INTO "products" ("id", "name", "description", "price", "stock", "isdeleted", "version")
                                      VALUES (@Id, @Name, @Description, @Price, @Stock, false, 1)
                                      """;
            await this._dbConnection.ExecuteAsync(productSql, product, transaction);

            if (product.SalesRecords.Any())
            {
                await this.PersistSalesAsync(product, transaction);
            }

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
                                          "stock" = @Stock,
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

            if (product.SalesRecords.Any())
            {
                await this.PersistSalesAsync(product, transaction);
            }

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
                           SELECT p.*, ps.*
                           FROM "products" AS p
                           LEFT JOIN "productsales" AS ps ON p."id" = ps."productid"
                           WHERE p."isdeleted" = false
                           """;

        var productDictionary = new Dictionary<Guid, Product>();

        var products = await this._dbConnection.QueryAsync<Product, ProductSaleRecord, Product>(
                           sql,
                           (product, sale) =>
                           {
                               if (!productDictionary.TryGetValue(product.Id, out var currentProduct))
                               {
                                   currentProduct = product;
                                   productDictionary.Add(currentProduct.Id, currentProduct);
                               }

                               if (sale != null)
                               {
                                   var salesList = (List<ProductSaleRecord>)currentProduct.GetType()
                                                                                    .GetField(
                                                                                        "_sales", BindingFlags.NonPublic | BindingFlags.Instance)
                                                                                    ?.GetValue(currentProduct);

                                   if (salesList != null && salesList.All(s => s.OrderId != sale.OrderId))
                                   {
                                       salesList.Add(sale);
                                   }
                               }

                               return currentProduct;
                           },
                           splitOn: "ProductId"
                       );

        return productDictionary.Values;
    }

    private async Task LoadSalesAsync(Product product)
    {
        const string salesSql = """
                                SELECT * FROM "productsales"
                                WHERE "productid" = @ProductId
                                """;
        var sales = await this._dbConnection.QueryAsync<ProductSaleRecord>(salesSql, new
        {
            ProductId = product.Id
        });

        var salesList = typeof(Product).GetField("_sales", BindingFlags.NonPublic | BindingFlags.Instance);
        if (salesList is not null)
        {
            salesList.SetValue(product, sales.ToList());
        }
    }

    private async Task PersistSalesAsync(Product product, IDbTransaction transaction)
    {
        const string salesSql = """
                                INSERT INTO "productsales" ("productid", "orderid", "quantity", "saledate")
                                VALUES (@ProductId, @OrderId, @Quantity, @SaleDate)
                                """;
        var salesWithProductId = product.SalesRecords.Select(s => new
        {
            ProductId = product.Id,
            s.OrderId,
            s.Quantity,
            s.SaleDate
        });
        await this._dbConnection.ExecuteAsync(salesSql, salesWithProductId, transaction);
    }
}