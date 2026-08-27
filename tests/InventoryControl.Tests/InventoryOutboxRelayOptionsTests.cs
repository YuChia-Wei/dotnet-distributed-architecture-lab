using InventoryControl.Infrastructure.BuildingBlocks;
using Microsoft.Extensions.Configuration;
using Shouldly;

namespace InventoryControl.Tests;

public sealed class InventoryOutboxRelayOptionsTests
{
    [Fact]
    public void given_no_retention_settings_when_configuration_is_parsed_then_rows_are_retained_without_limit()
    {
        var configuration = Configuration(new Dictionary<string, string?>());

        var options = InventoryOutboxRelayOptions.FromConfiguration(configuration);

        options.RetentionMode.ShouldBe(InventoryOutboxRetentionMode.RetainAll);
        options.PublishedRetentionDays.ShouldBeNull();
    }

    [Fact]
    public void given_finite_retention_without_positive_days_when_configuration_is_parsed_then_startup_fails()
    {
        var configuration = Configuration(new Dictionary<string, string?>
        {
            ["Messaging:OutboxRelay:Retention:Mode"] = "PublishedForDays",
            ["Messaging:OutboxRelay:Retention:PublishedRetentionDays"] = "0"
        });

        var exception = Should.Throw<InvalidOperationException>(
            () => InventoryOutboxRelayOptions.FromConfiguration(configuration));

        exception.Message.ShouldContain("PublishedRetentionDays");
    }

    private static IConfiguration Configuration(Dictionary<string, string?> values)
        => new ConfigurationBuilder().AddInMemoryCollection(values).Build();
}
