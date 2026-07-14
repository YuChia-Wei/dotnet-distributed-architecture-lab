using System.Data;
using Dapper;
using SaleOrders.Applications.Queries;

namespace SaleOrders.Infrastructure.Applications.Repositories;

/// <summary>Reads Orders projections without rehydrating event-sourced aggregates.</summary>
public sealed class OrderQueryRepository(IDbConnection dbConnection) : IOrderQueryRepository
{
    /// <inheritdoc />
    public Task<OrderReadModel?> FindByIdAsync(
        Guid id,
        CancellationToken cancellationToken = default)
    {
        const string sql = @"
        SELECT Id, OrderDate, TotalAmount, ProductId, ProductName, Quantity
        FROM Orders
        WHERE Id = @Id";

        return dbConnection.QuerySingleOrDefaultAsync<OrderReadModel>(
            new CommandDefinition(
                sql,
                new { Id = id },
                cancellationToken: cancellationToken));
    }

    /// <inheritdoc />
    public async Task<IReadOnlyList<OrderReadModel>> FindAllAsync(
        CancellationToken cancellationToken = default)
    {
        const string sql = @"
        SELECT Id, OrderDate, TotalAmount, ProductId, ProductName, Quantity
        FROM Orders
        ORDER BY OrderDate DESC, Id";

        var orders = await dbConnection.QueryAsync<OrderReadModel>(
            new CommandDefinition(sql, cancellationToken: cancellationToken));
        return orders.AsList();
    }
}
