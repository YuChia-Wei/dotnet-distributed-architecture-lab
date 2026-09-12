namespace SaleOrders.Applications.Diagnostics;

/// <summary>在介接器的保留期間內，每筆診斷請求只計算一次。</summary>
public interface IParallelStatisticsWriter
{
    /// <summary>執行作業並傳遞取消要求。</summary>
    Task RecordAsync(Guid probeId, CancellationToken cancellationToken);
}
