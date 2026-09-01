namespace SaleProducts.WebApi.Models.Responses;

/// <summary>Response returned after accepting a consumer exception policy probe.</summary>
/// <param name="ProbeId">Stable identifier for correlating retry and dead-letter evidence.</param>
/// <param name="FailureKind">The requested exception branch.</param>
/// <param name="Topic">The Kafka topic that carries the probe.</param>
/// <param name="Consumer">The consumer host that deliberately handles the probe.</param>
public sealed record ConsumerExceptionPolicyProbeResponse(
    Guid ProbeId,
    string FailureKind,
    string Topic,
    string Consumer);
