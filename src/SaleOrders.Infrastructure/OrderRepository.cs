using Dapper;
using Npgsql;
using SaleOrders.Applications;
using SaleOrders.Domains;

namespace SaleOrders.Infrastructure;

public class OrderRepository : IOrderRepository
{
    private readonly string _connectionString;

    public OrderRepository(string connectionString)
    {
        _connectionString = connectionString;
    }

    public async Task<Order?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default)
    {
        await using var connection = new NpgsqlConnection(_connectionString);
        const string sql = "SELECT * FROM Orders WHERE Id = @Id";
        return await connection.QuerySingleOrDefaultAsync<Order>(sql, new { Id = id });
    }

    public async Task<IEnumerable<Order>> GetAllAsync(CancellationToken cancellationToken = default)
    {
        await using var connection = new NpgsqlConnection(_connectionString);
        const string sql = "SELECT * FROM Orders";
        return await connection.QueryAsync<Order>(sql);
    }

    public async Task AddAsync(Order order, CancellationToken cancellationToken = default)
    {
        await using var connection = new NpgsqlConnection(_connectionString);
        const string sql = "INSERT INTO Orders (Id, OrderDate, TotalAmount) VALUES (@Id, @OrderDate, @TotalAmount)";
        await connection.ExecuteAsync(sql, order);
    }

    public async Task UpdateAsync(Order order, CancellationToken cancellationToken = default)
    {
        await using var connection = new NpgsqlConnection(_connectionString);
        const string sql = "UPDATE Orders SET OrderDate = @OrderDate, TotalAmount = @TotalAmount WHERE Id = @Id";
        await connection.ExecuteAsync(sql, order);
    }

    public async Task DeleteAsync(Guid id, CancellationToken cancellationToken = default)
    {
        await using var connection = new NpgsqlConnection(_connectionString);
        const string sql = "DELETE FROM Orders WHERE Id = @Id";
        await connection.ExecuteAsync(sql, new { Id = id });
    }
}