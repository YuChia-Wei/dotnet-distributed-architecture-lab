using Lab.BuildingBlocks.Integrations;
using Lab.BuildingBlocks.Integrations.Diagnostics;

namespace SaleProducts.Applications.UseCases;

/// <summary>明確啟用後，發佈選定範例的外部事件。</summary>
public sealed class TriggerParallelWorkProbeUseCase(ParallelWorkProbeOptions options,
    IIntegrationEventPublisher publisher) : ITriggerParallelWorkProbeUseCase
{
    /// <inheritdoc />
    public async Task<TriggerParallelWorkProbeOutput> ExecuteAsync(TriggerParallelWorkProbeInput input,
        CancellationToken cancellationToken)
    {
        ArgumentNullException.ThrowIfNull(input);
        cancellationToken.ThrowIfCancellationRequested();
        if (!Enum.IsDefined(input.Mode)) throw new ArgumentOutOfRangeException(nameof(input));
        if (input.ProbeId == Guid.Empty) throw new ArgumentException("ProbeId must not be empty.", nameof(input));
        if (!options.Enabled) return new TriggerParallelWorkProbeOutput(false, null);

        var id = input.ProbeId ?? Guid.CreateVersion7();
        IIntegrationEvent message = input.Mode == ParallelWorkProbeMode.WhenAll
            ? new WhenAllWorkRequested(id, DateTime.UtcNow)
            : new IndependentWorkRequested(id, DateTime.UtcNow);
        await publisher.PublishAsync(message);
        return new TriggerParallelWorkProbeOutput(true, id);
    }
}
