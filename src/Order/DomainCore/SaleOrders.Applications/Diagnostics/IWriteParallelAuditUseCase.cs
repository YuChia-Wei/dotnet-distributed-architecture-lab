namespace SaleOrders.Applications.Diagnostics;

/// <summary>獨立於統計資料記錄診斷稽核。</summary>
public interface IWriteParallelAuditUseCase
{
    /// <summary>執行作業並傳遞取消要求。</summary>
    Task ExecuteAsync(ParallelWorkInput input, CancellationToken cancellationToken);
}
