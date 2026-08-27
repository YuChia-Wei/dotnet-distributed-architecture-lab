using Microsoft.Extensions.Configuration;

namespace InventoryControl.Infrastructure.BuildingBlocks;

public enum InventoryOutboxRetentionMode
{
    RetainAll,
    PublishedForDays
}

/// <summary>Runtime configuration for the Inventory source-outbox relay and published-row retention.</summary>
public sealed record InventoryOutboxRelayOptions(
    bool Enabled,
    InventoryOutboxRetentionMode RetentionMode,
    int? PublishedRetentionDays)
{
    public const string SectionName = "Messaging:OutboxRelay";

    public static InventoryOutboxRelayOptions FromConfiguration(IConfiguration configuration)
    {
        var section = configuration.GetSection(SectionName);
        var rawMode = section["Retention:Mode"] ?? nameof(InventoryOutboxRetentionMode.RetainAll);
        if (!Enum.TryParse<InventoryOutboxRetentionMode>(rawMode, true, out var mode))
        {
            throw new InvalidOperationException(
                $"{SectionName}:Retention:Mode must be RetainAll or PublishedForDays.");
        }

        var days = section.GetValue<int?>("Retention:PublishedRetentionDays");
        if (mode == InventoryOutboxRetentionMode.PublishedForDays && days is not > 0)
        {
            throw new InvalidOperationException(
                $"{SectionName}:Retention:PublishedRetentionDays must be greater than zero when retention is PublishedForDays.");
        }

        return new InventoryOutboxRelayOptions(
            section.GetValue("Enabled", false),
            mode,
            days);
    }
}
