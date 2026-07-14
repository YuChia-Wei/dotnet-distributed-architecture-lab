namespace Lab.BuildingBlocks.Integrations;

/// <summary>Transport-neutral metadata that must remain stable across delivery retries.</summary>
public sealed record IntegrationMessageDelivery(Guid MessageId, string? PartitionKey = null);
