using System.Text.Json.Serialization;

namespace Lab.BuildingBlocks.Integrations.Diagnostics;

/// <summary>Identifies the exception branch exercised by a consumer policy probe.</summary>
[JsonConverter(typeof(JsonStringEnumConverter<ConsumerExceptionPolicyProbeFailureKind>))]
public enum ConsumerExceptionPolicyProbeFailureKind
{
    /// <summary>Exercises the transient timeout policy.</summary>
    Timeout,

    /// <summary>Exercises the unclassified exception fallback policy.</summary>
    Unhandled,
}

/// <summary>A lab-only integration event that deliberately fails in a consumer.</summary>
/// <param name="ProbeId">Stable identifier used to correlate every delivery attempt.</param>
/// <param name="FailureKind">The exception branch to exercise.</param>
/// <param name="OccurredOn">The time at which the probe was requested.</param>
public sealed record ConsumerExceptionPolicyProbe(
    Guid ProbeId,
    ConsumerExceptionPolicyProbeFailureKind FailureKind,
    DateTime OccurredOn) : IIntegrationEvent;
