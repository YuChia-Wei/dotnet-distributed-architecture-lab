using Microsoft.Extensions.Logging;
using SaleOrders.Applications.Diagnostics;

namespace SaleOrders.Consumer.Diagnostics;

/// <summary>模擬範例中的獨立非同步統計作業。</summary>
public sealed class DemoParallelStatisticsWriter(ParallelWorkStore store, ParallelWorkScope scope,
    ILogger<DemoParallelStatisticsWriter> logger) : IParallelStatisticsWriter
{
    /// <inheritdoc />
    public async Task RecordAsync(Guid probeId, CancellationToken cancellationToken)
    {
        logger.LogInformation("Parallel work {ProbeId} statistics started in scope {ScopeId}", probeId, scope.Id);
        await Task.Delay(TimeSpan.FromMilliseconds(700), cancellationToken);
        var added = store.RecordStatistics(probeId);
        logger.LogInformation("Parallel work {ProbeId} statistics completed in scope {ScopeId}; applied={Applied}", probeId, scope.Id, added);
    }
}
