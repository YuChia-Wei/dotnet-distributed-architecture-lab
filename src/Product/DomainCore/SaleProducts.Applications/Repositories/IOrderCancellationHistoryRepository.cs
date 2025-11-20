namespace SaleProducts.Applications.Repositories;

/// <summary>
/// 訂單取消事件處理記錄的儲存介面。
/// </summary>
public interface IOrderCancellationHistoryRepository
{
    /// <summary>
    /// 檢查指定訂單取消事件是否已處理。
    /// </summary>
    /// <param name="orderId">訂單識別碼。</param>
    /// <returns>若已處理則為 <c>true</c>。</returns>
    Task<bool> HasProcessedAsync(Guid orderId);

    /// <summary>
    /// 標記指定訂單取消事件為已處理。
    /// </summary>
    /// <param name="orderId">訂單識別碼。</param>
    Task MarkProcessedAsync(Guid orderId);
}