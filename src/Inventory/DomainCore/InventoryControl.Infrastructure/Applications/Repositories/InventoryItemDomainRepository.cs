using System;
using System.Collections.Generic;
using System.Data;
using System.Threading;
using System.Threading.Tasks;
using Dapper;
using InventoryControl.Applications.Repositories;
using InventoryControl.Domains;
using Lab.BuildingBlocks.Domains;

namespace InventoryControl.Infrastructure.Applications.Repositories;

public class InventoryItemDomainRepository : IInventoryItemDomainRepository
{
    private readonly IDbConnection _dbConnection;
    private readonly IDomainEventDispatcher _dispatcher;

    public InventoryItemDomainRepository(IDbConnection dbConnection, IDomainEventDispatcher dispatcher)
    {
        this._dbConnection = dbConnection;
        this._dispatcher = dispatcher;
    }

    public async Task<InventoryItem?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default)
    {
        const string sql = "SELECT * FROM InventoryItems WHERE Id = @Id";
        return await this._dbConnection.QuerySingleOrDefaultAsync<InventoryItem>(sql, new
        {
            Id = id
        });
    }

    public async Task<IEnumerable<InventoryItem>> GetAllAsync(CancellationToken cancellationToken = default)
    {
        const string sql = "SELECT * FROM InventoryItems";
        return await this._dbConnection.QueryAsync<InventoryItem>(sql);
    }

    public async Task AddAsync(InventoryItem inventoryItem, CancellationToken cancellationToken = default)
    {
        const string sql =
            "INSERT INTO InventoryItems (Id, ProductId, Stock) VALUES (@Id, @ProductId, @Stock)";
        await this._dbConnection.ExecuteAsync(sql, inventoryItem);
        await this._dispatcher.DispatchAsync(inventoryItem.DomainEvents, cancellationToken);
    }

    public async Task UpdateAsync(InventoryItem inventoryItem, CancellationToken cancellationToken = default)
    {
        const string sql = "UPDATE InventoryItems SET Stock = @Stock WHERE Id = @Id";
        await this._dbConnection.ExecuteAsync(sql, inventoryItem);
    }

    public async Task<InventoryItem?> GetByProductIdAsync(Guid productId)
    {
        const string sql = "SELECT * FROM InventoryItems WHERE ProductId = @ProductId";
        return await this._dbConnection.QuerySingleOrDefaultAsync<InventoryItem>(sql, new
        {
            ProductId = productId
        });
    }

    public async Task DeleteAsync(Guid id, CancellationToken cancellationToken = default)
    {
        const string sql = "DELETE FROM InventoryItems WHERE Id = @Id";
        await this._dbConnection.ExecuteAsync(sql, new
        {
            Id = id
        });
    }
}