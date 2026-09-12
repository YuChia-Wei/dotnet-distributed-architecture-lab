namespace SaleOrders.Applications.Diagnostics;

/// <summary>驗證診斷輸入並記錄一次稽核副作用。</summary>
public sealed class WriteParallelAuditUseCase(IParallelAuditWriter writer) : IWriteParallelAuditUseCase
{
    /// <inheritdoc />
    public Task ExecuteAsync(ParallelWorkInput input, CancellationToken cancellationToken)
    {
        ArgumentNullException.ThrowIfNull(input);
        if (input.ProbeId == Guid.Empty) throw new ArgumentException("ProbeId must not be empty.", nameof(input));
        cancellationToken.ThrowIfCancellationRequested();
        return writer.WriteAsync(input.ProbeId, cancellationToken);
    }
}
