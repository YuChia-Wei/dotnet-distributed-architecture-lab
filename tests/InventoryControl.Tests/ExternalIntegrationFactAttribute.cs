namespace InventoryControl.Tests;

/// <summary>
/// Marks a test that needs a real service outside the test process.
/// </summary>
/// <remarks>
/// External integration tests are skipped unless both the explicit opt-in flag and
/// the required service configuration are present. This keeps ordinary test runs
/// deterministic while preserving an executable environment verification profile.
/// </remarks>
public sealed class ExternalIntegrationFactAttribute : FactAttribute
{
    public const string OptInVariable = "RUN_EXTERNAL_INTEGRATION_TESTS";
    public const string InventoryPostgresVariable = "INVENTORY_TEST_POSTGRES_CONNECTION_STRING";

    public ExternalIntegrationFactAttribute()
    {
        var optedIn = string.Equals(
            Environment.GetEnvironmentVariable(OptInVariable),
            "true",
            StringComparison.OrdinalIgnoreCase);
        var connectionString = Environment.GetEnvironmentVariable(InventoryPostgresVariable);

        if (!optedIn || string.IsNullOrWhiteSpace(connectionString))
        {
            this.Skip = $"External integration test. Set {OptInVariable}=true and {InventoryPostgresVariable} to opt in.";
        }
    }
}
