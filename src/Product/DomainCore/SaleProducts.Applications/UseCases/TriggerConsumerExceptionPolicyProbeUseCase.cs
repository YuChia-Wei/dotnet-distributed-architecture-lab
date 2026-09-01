using Lab.BuildingBlocks.Integrations;
using Lab.BuildingBlocks.Integrations.Diagnostics;

namespace SaleProducts.Applications.UseCases;

/// <summary>Configuration for the lab-only consumer exception policy probe.</summary>
/// <param name="Enabled">Whether probe publication is allowed.</param>
public sealed record ConsumerExceptionPolicyProbeOptions(bool Enabled)
{
    /// <summary>Configuration key used by runtime hosts.</summary>
    public const string EnabledConfigurationKey = "Diagnostics:ConsumerExceptionPolicyProbe:Enabled";
}

/// <summary>Input for triggering a consumer exception policy probe.</summary>
/// <param name="FailureKind">The exception branch to exercise.</param>
public sealed record TriggerConsumerExceptionPolicyProbeInput(
    ConsumerExceptionPolicyProbeFailureKind FailureKind);

/// <summary>Result status for a consumer exception policy probe request.</summary>
public enum TriggerConsumerExceptionPolicyProbeStatus
{
    /// <summary>The diagnostic capability is disabled.</summary>
    Disabled,

    /// <summary>The probe was accepted for asynchronous delivery.</summary>
    Accepted,
}

/// <summary>Output returned after requesting a consumer exception policy probe.</summary>
/// <param name="Status">Whether the request was accepted.</param>
/// <param name="ProbeId">The stable probe identifier when accepted.</param>
/// <param name="FailureKind">The requested exception branch.</param>
public sealed record TriggerConsumerExceptionPolicyProbeOutput(
    TriggerConsumerExceptionPolicyProbeStatus Status,
    Guid? ProbeId,
    ConsumerExceptionPolicyProbeFailureKind FailureKind);

/// <summary>Inbound port for publishing a lab-only consumer exception policy probe.</summary>
public interface ITriggerConsumerExceptionPolicyProbeUseCase
{
    /// <summary>Publishes a probe when the diagnostic capability is enabled.</summary>
    Task<TriggerConsumerExceptionPolicyProbeOutput> ExecuteAsync(
        TriggerConsumerExceptionPolicyProbeInput input,
        CancellationToken cancellationToken);
}

/// <summary>Publishes a lab-only integration event used to exercise consumer failure policies.</summary>
public sealed class TriggerConsumerExceptionPolicyProbeUseCase(
    ConsumerExceptionPolicyProbeOptions options,
    IIntegrationEventPublisher publisher) : ITriggerConsumerExceptionPolicyProbeUseCase
{
    /// <inheritdoc />
    public async Task<TriggerConsumerExceptionPolicyProbeOutput> ExecuteAsync(
        TriggerConsumerExceptionPolicyProbeInput input,
        CancellationToken cancellationToken)
    {
        cancellationToken.ThrowIfCancellationRequested();

        if (!options.Enabled)
        {
            return new TriggerConsumerExceptionPolicyProbeOutput(
                TriggerConsumerExceptionPolicyProbeStatus.Disabled,
                null,
                input.FailureKind);
        }

        var probe = new ConsumerExceptionPolicyProbe(
            Guid.CreateVersion7(),
            input.FailureKind,
            DateTime.UtcNow);

        await publisher.PublishAsync(probe);

        return new TriggerConsumerExceptionPolicyProbeOutput(
            TriggerConsumerExceptionPolicyProbeStatus.Accepted,
            probe.ProbeId,
            probe.FailureKind);
    }
}
