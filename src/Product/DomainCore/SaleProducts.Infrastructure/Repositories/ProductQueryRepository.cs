using System.Data;
using Dapper;
using SaleProducts.Applications.Dtos;
using SaleProducts.Applications.Queries;

namespace SaleProducts.Infrastructure.Repositories;

public class ProductQueryRepository : IProductQueryRepository
{
    private readonly IDbConnection _dbConnection;

    public ProductQueryRepository(IDbConnection dbConnection)
    {
        this._dbConnection = dbConnection;
    }

    public async Task<IReadOnlyList<ProductDto>> GetAllAsync(CancellationToken cancellationToken = default)
    {
        const string sql = """
                           SELECT
                               p."id" AS Id,
                               p."name" AS Name,
                               p."description" AS Description,
                               p."price" AS Price
                           FROM "products" AS p
                           WHERE p."isdeleted" = false
                           """;

        var items = await this._dbConnection.QueryAsync<ProductDto>(sql);
        return items.ToList();
    }

    public async Task<ProductDto?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default)
    {
        const string sql = """
                           SELECT
                               p."id" AS Id,
                               p."name" AS Name,
                               p."description" AS Description,
                               p."price" AS Price
                           FROM "products" AS p
                           WHERE p."id" = @Id AND p."isdeleted" = false
                           """;
        return await this._dbConnection.QueryFirstOrDefaultAsync<ProductDto>(sql, new
        {
            Id = id
        });
    }
}
