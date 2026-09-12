namespace SaleOrders.Applications.Diagnostics;

/// <summary>獨立於稽核資料記錄診斷統計。</summary>
public interface IRecordParallelStatisticsUseCase
{
    /// <summary>執行作業並傳遞取消要求。</summary>
    Task ExecuteAsync(ParallelWorkInput input, CancellationToken cancellationToken);
}
