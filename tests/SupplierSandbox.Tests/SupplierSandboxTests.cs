using Dapper;
using Npgsql;

public sealed class SupplierSandboxTests : IAsyncLifetime
{
    private readonly NpgsqlDataSource dataSource = NpgsqlDataSource.Create(Environment.GetEnvironmentVariable("SUPPLIER_TEST_POSTGRES_CONNECTION_STRING") ?? "Host=localhost;Database=unconfigured_supplier_test;Username=postgres;Password=postgres");
    private readonly SupplierStore store;
    private readonly string? connectionString = Environment.GetEnvironmentVariable("SUPPLIER_TEST_POSTGRES_CONNECTION_STRING");

    public SupplierSandboxTests() => store = new SupplierStore(dataSource);

    [Fact]
    [Trait("Scenario", "S01")]
    public async Task S01_Given_a_dedicated_postgres_store_When_the_same_supplier_key_is_replayed_Then_one_stable_order_is_returned_and_changed_payload_conflicts()
    {
        GivenPostgresIsOptedIn();
        var sku = $"TEST-{Guid.NewGuid():N}";
        var requestId = Guid.NewGuid();
        var concurrentRequestId = Guid.NewGuid();
        await GivenDedicatedSkuAsync(sku);
        try
        {
            var payload = new SupplierOrderRequest(requestId, sku, 3, 100m, "TWD");
            var first = await WhenSubmittingAsync(payload);
            var replay = await WhenSubmittingAsync(payload);
            var simultaneous = await Task.WhenAll(WhenSubmittingAsync(payload with { ClientRequestId = concurrentRequestId }), WhenSubmittingAsync(payload with { ClientRequestId = concurrentRequestId }));
            var changedQuantity = await WhenSubmittingAsync(payload with { Quantity = 4 });
            var changedPrice = await WhenSubmittingAsync(payload with { UnitPrice = 99m });
            var changedSku = await WhenSubmittingAsync(payload with { Sku = "UNKNOWN-01" });
            var changedCurrency = await WhenSubmittingAsync(payload with { Currency = "USD" });
            ThenReplayKeepsTheSameSupplierOrder(first, replay);
            ThenReplayKeepsTheSameSupplierOrder(simultaneous[0], simultaneous[1]);
            ThenChangedPayloadConflicts(changedQuantity);
            ThenChangedPayloadConflicts(changedPrice);
            ThenChangedPayloadConflicts(changedSku);
            ThenChangedPayloadConflicts(changedCurrency);
        }
        finally { await CleanupAsync(sku, requestId); await CleanupAsync(sku, concurrentRequestId); }
    }

    [Fact]
    [Trait("Scenario", "S07")]
    public void S07_Given_the_supplier_SKU_rule_When_values_are_checked_Then_only_bounded_vendor_SKUs_are_accepted()
    {
        GivenCandidateSkuValues(out var valid, out var invalid);
        var actual = WhenCheckingSku(valid, invalid);
        ThenSkuValidationMatchesTheContract(actual);
    }

    private void GivenPostgresIsOptedIn()
    {
        if (string.IsNullOrWhiteSpace(connectionString)) Assert.Skip("Set SUPPLIER_TEST_POSTGRES_CONNECTION_STRING to run the real PostgreSQL supplier idempotency scenario.");
    }
    private static void GivenCandidateSkuValues(out string valid, out string[] invalid) { valid = "REAL_01-x"; invalid = ["", " ", "bad/sku", new string('x', 65)]; }
    private async Task GivenDedicatedSkuAsync(string sku)
    {
        var source = dataSource;
        await using var c = await source.OpenConnectionAsync();
        await c.ExecuteAsync("CREATE TABLE IF NOT EXISTS supplier_skus (sku varchar(64) PRIMARY KEY,name varchar(120) NOT NULL,unit_price numeric(12,2) NOT NULL,currency char(3) NOT NULL,order_allowed boolean NOT NULL DEFAULT true)");
        await c.ExecuteAsync("CREATE TABLE IF NOT EXISTS supplier_orders (supplier_order_id uuid PRIMARY KEY,client_request_id uuid NOT NULL UNIQUE,sku varchar(64) NOT NULL,quantity integer NOT NULL,unit_price numeric(12,2) NOT NULL,currency char(3) NOT NULL,status varchar(16) NOT NULL,created_at timestamptz NOT NULL DEFAULT now())");
        await c.ExecuteAsync("INSERT INTO supplier_skus(sku,name,unit_price,currency,order_allowed) VALUES(@sku,'test',100,'TWD',true)", new { sku });
    }
    private Task<(SupplierOrderResponse? Order, bool Conflict)> WhenSubmittingAsync(SupplierOrderRequest request) => store.CreateOrReplayAsync(request, CancellationToken.None);
    private static (bool Valid, bool[] Invalid) WhenCheckingSku(string valid, string[] invalid) => (SupplierStore.IsValidSku(valid), invalid.Select(SupplierStore.IsValidSku).ToArray());
    private static void ThenReplayKeepsTheSameSupplierOrder((SupplierOrderResponse? Order, bool Conflict) first, (SupplierOrderResponse? Order, bool Conflict) replay)
    {
        Assert.False(first.Conflict); Assert.False(replay.Conflict); Assert.NotNull(first.Order); Assert.NotNull(replay.Order);
        Assert.Equal(first.Order.SupplierOrderId, replay.Order.SupplierOrderId); Assert.Equal("accepted", replay.Order.Status);
    }
    private static void ThenChangedPayloadConflicts((SupplierOrderResponse? Order, bool Conflict) result) { Assert.True(result.Conflict); Assert.Null(result.Order); }
    private static void ThenSkuValidationMatchesTheContract((bool Valid, bool[] Invalid) result) { Assert.True(result.Valid); Assert.All(result.Invalid, Assert.False); }
    private async Task CleanupAsync(string sku, Guid requestId)
    {
        await using var c = await dataSource.OpenConnectionAsync();
        await c.ExecuteAsync("DELETE FROM supplier_orders WHERE client_request_id=@requestId", new { requestId });
        await c.ExecuteAsync("DELETE FROM supplier_skus WHERE sku=@sku", new { sku });
    }
    public ValueTask InitializeAsync() => ValueTask.CompletedTask;
    public ValueTask DisposeAsync() => dataSource.DisposeAsync();
}
