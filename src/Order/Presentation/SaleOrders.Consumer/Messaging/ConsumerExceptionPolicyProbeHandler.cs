using Lab.BuildingBlocks.Integrations.Diagnostics;
using Microsoft.Extensions.Logging;

namespace SaleOrders.Consumer.Messaging;

/// <summary>Deliberately throws exceptions so the lab can demonstrate Wolverine failure policies.</summary>
public sealed class ConsumerExceptionPolicyProbeHandler
{
    /// <summary>Throws the exception selected by the probe.</summary>
    public static void Handle(
        ConsumerExceptionPolicyProbe probe,
        ILogger<ConsumerExceptionPolicyProbeHandler> logger)
    {
        logger.LogWarning(
            "Consumer exception policy probe {ProbeId} is throwing {FailureKind}",
            probe.ProbeId,
            probe.FailureKind);

        throw probe.FailureKind switch
        {
            ConsumerExceptionPolicyProbeFailureKind.Timeout =>
                new TimeoutException($"Consumer exception policy timeout probe {probe.ProbeId}."),
            ConsumerExceptionPolicyProbeFailureKind.Unhandled =>
                new InvalidOperationException($"Consumer exception policy unhandled probe {probe.ProbeId}."),
            _ => new ArgumentOutOfRangeException(
                nameof(probe),
                probe.FailureKind,
                "Unsupported consumer exception policy probe failure kind."),
        };
    }
}
