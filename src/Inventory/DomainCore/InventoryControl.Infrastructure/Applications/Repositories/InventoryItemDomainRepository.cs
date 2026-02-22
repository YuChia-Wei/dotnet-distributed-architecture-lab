using System;
using System.Collections.Generic;
using System.Data;
using System.Threading;
using System.Threading.Tasks;
using Dapper;
using InventoryControl.Applications.Repositories;
using InventoryControl.Domains;
using Lab.BuildingBlocks.Application;
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

    public async Task<InventoryItem?> FindByIdAsync(Guid id, CancellationToken cancellationToken = default)
    {
        const string sql = "SELECT * FROM InventoryItems WHERE Id = @Id";
        return await this._dbConnection.QuerySingleOrDefaultAsync<InventoryItem>(sql, new
        {
            Id = id
        });
    }

    public async Task<IEnumerable<InventoryItem>> FindByIdsAsync(IEnumerable<Guid> ids, CancellationToken cancellationToken = default)
    {
        throw new NotImplementedException();
    }

    public async Task SaveAsync(InventoryItem entity, CancellationToken cancellationToken = default)
    {
        // 嘗試更新，若無影響列數則新增
        const string updateSql = "UPDATE InventoryItems SET Stock = @Stock WHERE Id = @Id";
        var affected = await this._dbConnection.ExecuteAsync(updateSql, entity);

        if (affected == 0)
        {
            const string insertSql =
                "INSERT INTO InventoryItems (Id, ProductId, Stock) VALUES (@Id, @ProductId, @Stock)";
            await this._dbConnection.ExecuteAsync(insertSql, entity);
        }

        await this._dispatcher.DispatchAsync(entity.DomainEvents, cancellationToken);
    }

    public async Task SaveAllAsync(IEnumerable<InventoryItem> entities, CancellationToken cancellationToken = default)
    {
        throw new NotImplementedException();
    }

    public async Task DeleteAsync(InventoryItem entity, CancellationToken cancellationToken = default)
    {
        const string sql = "DELETE FROM InventoryItems WHERE Id = @Id";
        await this._dbConnection.ExecuteAsync(sql, new
        {
            Id = entity.Id
        });
    }

    public async Task<InventoryItem?> GetByProductIdAsync(Guid productId)
    {
        const string sql = "SELECT * FROM InventoryItems WHERE ProductId = @ProductId";
        return await this._dbConnection.QuerySingleOrDefaultAsync<InventoryItem>(sql, new
        {
            ProductId = productId
        });
    }
}