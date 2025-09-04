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
        _dbConnection = dbConnection;
    }

    public async Task<Product?> GetByIdAsync(Guid id)
    {
        const string productSql = """
                                  SELECT * FROM "Products"
                                  WHERE "Id" = @Id AND "IsDeleted" = false
                                  """;
        var product = await _dbConnection.QueryFirstOrDefaultAsync<Product>(productSql, new { Id = id });

        if (product is not null)
        {
            await LoadSalesAsync(product);
        }

        return product;
    }

    public async Task AddAsync(Product product)
    {
        if (_dbConnection.State != ConnectionState.Open)
        {
            _dbConnection.Open();
        }
        using var transaction = _dbConnection.BeginTransaction();

        try
        {
            const string productSql = """
                                      INSERT INTO "Products" ("Id", "Name", "Description", "Price", "Stock", "IsDeleted", "Version")
                                      VALUES (@Id, @Name, @Description, @Price, @Stock, false, 1)
                                      """;
            await _dbConnection.ExecuteAsync(productSql, product, transaction);

            if (product.Sales.Any())
            {
                await PersistSalesAsync(product, transaction);
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
        if (_dbConnection.State != ConnectionState.Open)
        {
            _dbConnection.Open();
        }
        using var transaction = _dbConnection.BeginTransaction();
        try
        {
            const string productSql = """
                                      UPDATE "Products"
                                      SET "Name" = @Name,
                                          "Description" = @Description,
                                          "Price" = @Price,
                                          "Stock" = @Stock,
                                          "Version" = "Version" + 1
                                      WHERE "Id" = @Id AND "Version" = @Version
                                      """;
            var affectedRows = await _dbConnection.ExecuteAsync(productSql, product, transaction);
            if (affectedRows == 0)
            {
                throw new DBConcurrencyException("The record has been modified by another user.");
            }
            
            const string deleteSalesSql = """DELETE FROM "ProductSales" WHERE "ProductId" = @ProductId""";
            await _dbConnection.ExecuteAsync(deleteSalesSql, new { ProductId = product.Id }, transaction);

            if (product.Sales.Any())
            {
                await PersistSalesAsync(product, transaction);
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
                           SELECT p.*, ps.*
                           FROM "Products" AS p
                           LEFT JOIN "ProductSales" AS ps ON p."Id" = ps."ProductId"
                           WHERE p."IsDeleted" = false
                           """;

        var productDictionary = new Dictionary<Guid, Product>();

        var products = await _dbConnection.QueryAsync<Product, ProductSale, Product>(
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
                    var salesList = (List<ProductSale>)currentProduct.GetType()
                        .GetField("_sales", BindingFlags.NonPublic | BindingFlags.Instance)
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
                                SELECT * FROM "ProductSales"
                                WHERE "ProductId" = @ProductId
                                """;
        var sales = await _dbConnection.QueryAsync<ProductSale>(salesSql, new { ProductId = product.Id });

        var salesList = typeof(Product).GetField("_sales", BindingFlags.NonPublic | BindingFlags.Instance);
        if (salesList is not null)
        {
            salesList.SetValue(product, sales.ToList());
        }
    }
    
    private async Task PersistSalesAsync(Product product, IDbTransaction transaction)
    {
        const string salesSql = """
                                INSERT INTO "ProductSales" ("ProductId", "OrderId", "Quantity", "SaleDate")
                                VALUES (@ProductId, @OrderId, @Quantity, @SaleDate)
                                """;
        var salesWithProductId = product.Sales.Select(s => new
        {
            ProductId = product.Id,
            s.OrderId,
            s.Quantity,
            s.SaleDate
        });
        await _dbConnection.ExecuteAsync(salesSql, salesWithProductId, transaction);
    }
}
