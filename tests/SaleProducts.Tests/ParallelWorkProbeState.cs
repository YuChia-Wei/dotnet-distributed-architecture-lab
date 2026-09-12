using System.Collections.Concurrent;
using SaleOrders.Applications.Diagnostics;
using SaleOrders.Consumer.Diagnostics;

namespace SaleProducts.Tests;

public sealed class ParallelWorkProbeState
{
    public ConcurrentDictionary<Guid, ParallelProbe> Probes { get; } = new();
    public ParallelWorkStore Store { get; } = new();

    public ParallelProbe GivenProbe(bool failStatisticsOnce = false)
    {
        var probe = new ParallelProbe { FailStatisticsOnce = failStatisticsOnce };
        this.Probes[probe.Id] = probe;
        return probe;
    }
}

public sealed class ParallelProbe
{
    public Guid Id { get; } = Guid.NewGuid();
    public bool FailStatisticsOnce { get; init; }
    public bool ThrowStatisticsSynchronously { get; init; }
    public int AuditAttempts;
    public int StatisticsAttempts;
    public ConcurrentBag<Guid> AuditScopes { get; } = new();
    public ConcurrentBag<Guid> StatisticsScopes { get; } = new();
    public ConcurrentBag<Guid> DisposedScopes { get; } = new();
    public TaskCompletionSource AuditStarted { get; } = new(TaskCreationOptions.RunContinuationsAsynchronously);
    public TaskCompletionSource StatisticsStarted { get; } = new(TaskCreationOptions.RunContinuationsAsynchronously);
    public TaskCompletionSource AuditRelease { get; } = new(TaskCreationOptions.RunContinuationsAsynchronously);
    public TaskCompletionSource StatisticsRelease { get; } = new(TaskCreationOptions.RunContinuationsAsynchronously);
    public TaskCompletionSource AuditCompleted { get; } = new(TaskCreationOptions.RunContinuationsAsynchronously);
    public TaskCompletionSource StatisticsCompleted { get; } = new(TaskCreationOptions.RunContinuationsAsynchronously);

    public Task WhenBothStartedAsync() => Task.WhenAll(this.AuditStarted.Task, this.StatisticsStarted.Task)
        .WaitAsync(TimeSpan.FromSeconds(20), TestContext.Current.CancellationToken);

    public Task WhenBothCompletedAsync() => Task.WhenAll(this.AuditCompleted.Task, this.StatisticsCompleted.Task)
        .WaitAsync(TimeSpan.FromSeconds(20), TestContext.Current.CancellationToken);

    public void ReleaseBoth()
    {
        this.AuditRelease.TrySetResult();
        this.StatisticsRelease.TrySetResult();
    }
}

public sealed class GatedAuditWriter(ParallelWorkProbeState state, ParallelWorkScope scope)
    : IParallelAuditWriter, IAsyncDisposable
{
    private ParallelProbe? probe;

    public async Task WriteAsync(Guid probeId, CancellationToken cancellationToken)
    {
        this.probe = state.Probes[probeId];
        Interlocked.Increment(ref this.probe.AuditAttempts);
        this.probe.AuditScopes.Add(scope.Id);
        this.probe.AuditStarted.TrySetResult();
        await this.probe.AuditRelease.Task.WaitAsync(cancellationToken);
        state.Store.WriteAudit(probeId);
        this.probe.AuditCompleted.TrySetResult();
    }

    public ValueTask DisposeAsync()
    {
        this.probe?.DisposedScopes.Add(scope.Id);
        return ValueTask.CompletedTask;
    }
}

public sealed class GatedStatisticsWriter(ParallelWorkProbeState state, ParallelWorkScope scope)
    : IParallelStatisticsWriter, IAsyncDisposable
{
    private ParallelProbe? probe;

    public Task RecordAsync(Guid probeId, CancellationToken cancellationToken)
    {
        this.probe = state.Probes[probeId];
        var attempt = Interlocked.Increment(ref this.probe.StatisticsAttempts);
        this.probe.StatisticsScopes.Add(scope.Id);
        this.probe.StatisticsStarted.TrySetResult();
        if (this.probe.ThrowStatisticsSynchronously) throw new InvalidOperationException("Synchronous diagnostic failure.");
        return this.CompleteAsync(probeId, attempt, cancellationToken);
    }

    private async Task CompleteAsync(Guid probeId, int attempt, CancellationToken cancellationToken)
    {
        await this.probe!.StatisticsRelease.Task.WaitAsync(cancellationToken);
        if (this.probe.FailStatisticsOnce && attempt == 1) throw new TimeoutException("Transient statistics failure.");
        state.Store.RecordStatistics(probeId);
        this.probe.StatisticsCompleted.TrySetResult();
    }

    public ValueTask DisposeAsync()
    {
        this.probe?.DisposedScopes.Add(scope.Id);
        return ValueTask.CompletedTask;
    }
}
