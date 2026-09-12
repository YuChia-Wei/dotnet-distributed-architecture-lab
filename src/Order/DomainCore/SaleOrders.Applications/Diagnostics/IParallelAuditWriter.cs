namespace SaleOrders.Applications.Diagnostics;

/// <summary>以冪等方式寫入診斷稽核紀錄。</summary>
public interface IParallelAuditWriter
{
    /// <summary>執行作業並傳遞取消要求。</summary>
    Task WriteAsync(Guid probeId, CancellationToken cancellationToken);
}
