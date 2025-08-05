using System.Data;
using Dapper;
using Lab.BuildingBlocks.Domains;
using SaleOrders.Applications.Repositories;
using SaleOrders.Domains;

namespace SaleOrders.Infrastructure.Applications.Repositories;

public class OrderDomainRepository : IOrderDomainRepository
{
    private readonly IDbConnection _dbConnection;
    private readonly IDomainEventDispatcher _dispatcher;

    public OrderDomainRepository(IDbConnection dbConnection, IDomainEventDispatcher dispatcher)
    {
        this._dbConnection = dbConnection;
        this._dispatcher = dispatcher;
    }

    public async Task<Order?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default)
    {
        const string sql = "SELECT * FROM Orders WHERE Id = @Id";
        return await this._dbConnection.QuerySingleOrDefaultAsync<Order>(sql, new
        {
            Id = id
        });
    }

    public async Task<IEnumerable<Order>> GetAllAsync(CancellationToken cancellationToken = default)
    {
        const string sql = "SELECT * FROM Orders";
        return await this._dbConnection.QueryAsync<Order>(sql);
    }

    public async Task AddAsync(Order order, CancellationToken cancellationToken = default)
    {
        const string sql =
            "INSERT INTO Orders (Id, OrderDate, TotalAmount, ProductName, Quantity) VALUES (@Id, @OrderDate, @TotalAmount, @ProductName, @Quantity)";
        await this._dbConnection.ExecuteAsync(sql, order);
        await this._dispatcher.DispatchAsync(order.DomainEvents, cancellationToken);
    }

    public async Task UpdateAsync(Order order, CancellationToken cancellationToken = default)
    {
        const string sql = "UPDATE Orders SET OrderDate = @OrderDate, TotalAmount = @TotalAmount WHERE Id = @Id";
        await this._dbConnection.ExecuteAsync(sql, order);
    }

    public async Task DeleteAsync(Guid id, CancellationToken cancellationToken = default)
    {
        const string sql = "DELETE FROM Orders WHERE Id = @Id";
        await this._dbConnection.ExecuteAsync(sql, new
        {
            Id = id
        });
    }
}