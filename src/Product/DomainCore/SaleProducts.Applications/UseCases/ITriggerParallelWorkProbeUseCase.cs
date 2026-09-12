namespace SaleProducts.Applications.UseCases;

/// <summary>透過既有整合事件發佈埠送出診斷事件。</summary>
public interface ITriggerParallelWorkProbeUseCase
{
    /// <summary>執行作業並傳遞取消要求。</summary>
    Task<TriggerParallelWorkProbeOutput> ExecuteAsync(TriggerParallelWorkProbeInput input,
        CancellationToken cancellationToken);
}
