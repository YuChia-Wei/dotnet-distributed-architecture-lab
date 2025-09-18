using System.Data;
using System.Threading;
using Dapper;
using SaleProducts.Applications.Repositories;

namespace SaleProducts.Infrastructure.Repositories;

/// <summary>
/// 使用 PostgreSQL 儲存訂單取消處理歷程。
/// </summary>
public class OrderCancellationHistoryRepository : IOrderCancellationHistoryRepository
{
    private readonly IDbConnection _dbConnection;
    private readonly SemaphoreSlim _initializationLock = new(1, 1);
    private bool _initialized;

    public OrderCancellationHistoryRepository(IDbConnection dbConnection)
    {
        this._dbConnection = dbConnection;
    }

    /// <summary>
    /// 取得指定訂單是否已被標記為處理完成。
    /// </summary>
    /// <param name="orderId">訂單識別碼。</param>
    /// <returns>若已處理則為 <c>true</c>。</returns>
    public async Task<bool> HasProcessedAsync(Guid orderId)
    {
        await this.EnsureInitializedAsync();

        const string sql = "SELECT 1 FROM \"ordercancellationhistory\" WHERE \"orderid\" = @OrderId";
        var result = await this._dbConnection.ExecuteScalarAsync<int?>(sql, new
        {
            OrderId = orderId
        });
        return result.HasValue;
    }

    /// <summary>
    /// 標記指定訂單取消事件為已完成處理。
    /// </summary>
    /// <param name="orderId">訂單識別碼。</param>
    public async Task MarkProcessedAsync(Guid orderId)
    {
        await this.EnsureInitializedAsync();

        const string sql = """
                           INSERT INTO "ordercancellationhistory" ("orderid", "processedat")
                           VALUES (@OrderId, @ProcessedAt)
                           ON CONFLICT ("orderid") DO NOTHING
                           """;

        await this._dbConnection.ExecuteAsync(sql, new
        {
            OrderId = orderId,
            ProcessedAt = DateTime.UtcNow
        });
    }

    private async Task EnsureInitializedAsync()
    {
        if (this._initialized)
        {
            return;
        }

        await this._initializationLock.WaitAsync();
        try
        {
            if (this._initialized)
            {
                return;
            }

            const string sql = """
                               CREATE TABLE IF NOT EXISTS "ordercancellationhistory"
                               (
                                   "orderid" UUID PRIMARY KEY,
                                   "processedat" TIMESTAMPTZ NOT NULL
                               )
                               """;
            await this._dbConnection.ExecuteAsync(sql);
            this._initialized = true;
        }
        finally
        {
            this._initializationLock.Release();
        }
    }
}
