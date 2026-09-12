using Microsoft.Extensions.Logging;
using SaleOrders.Applications.Diagnostics;

namespace SaleOrders.Consumer.Diagnostics;

/// <summary>模擬範例中的獨立非同步稽核作業。</summary>
public sealed class DemoParallelAuditWriter(ParallelWorkStore store, ParallelWorkScope scope,
    ILogger<DemoParallelAuditWriter> logger) : IParallelAuditWriter
{
    /// <inheritdoc />
    public async Task WriteAsync(Guid probeId, CancellationToken cancellationToken)
    {
        logger.LogInformation("Parallel work {ProbeId} audit started in scope {ScopeId}", probeId, scope.Id);
        await Task.Delay(TimeSpan.FromMilliseconds(500), cancellationToken);
        var added = store.WriteAudit(probeId);
        logger.LogInformation("Parallel work {ProbeId} audit completed in scope {ScopeId}; applied={Applied}", probeId, scope.Id, added);
    }
}
