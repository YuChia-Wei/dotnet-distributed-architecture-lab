using Dapper;
using Npgsql;
using NSubstitute;
using Procurement.Applications;
using Procurement.Domains;
using Procurement.Infrastructure;

namespace Procurement.Tests;

public sealed class PurchasePostgresScenarios
{
    // P02 / AC01: concurrent creators of one client key converge on one durable local identity.
    [ExternalIntegrationFact, Trait("Scenario", "P02")]
    public async Task Concurrent_matching_creates_store_one_purchase()
    {
        await using var dataSource = GivenDataSource();
        await GivenAdditiveSchema(dataSource);
        var store = new PostgresPurchaseStore(dataSource);
        var identity = GivenIdentity();
        var ids = new[] { Guid.NewGuid(), Guid.NewGuid() };
        try
        {
            var created = await WhenTwoCreatorsRace(store, identity, ids);
            await ThenOnePurchaseWasCommitted(dataSource, identity, created);
        }
        finally { await CleanupOwnRows(dataSource, identity.ClientRequestId); }
    }

    // P03 / AC01: persisted immutable identity is checked before any external submission.
    [ExternalIntegrationFact, Trait("Scenario", "P03-quantity")]
    public Task Changed_quantity_conflicts_against_postgres_without_supplier_call() =>
        ChangedIdentityConflictsWithoutSupplierCall("quantity");

    [ExternalIntegrationFact, Trait("Scenario", "P03-provider")]
    public Task Changed_provider_conflicts_against_postgres_without_supplier_call() =>
        ChangedIdentityConflictsWithoutSupplierCall("provider");

    [ExternalIntegrationFact, Trait("Scenario", "P03-product")]
    public Task Changed_product_conflicts_against_postgres_without_supplier_call() =>
        ChangedIdentityConflictsWithoutSupplierCall("product");

    private static async Task ChangedIdentityConflictsWithoutSupplierCall(string field)
    {
        await using var dataSource = GivenDataSource();
        await GivenAdditiveSchema(dataSource);
        var store = new PostgresPurchaseStore(dataSource);
        var identity = GivenIdentity();
        var orderId = Guid.NewGuid();
        var supplier = Substitute.For<ISupplierGateway>();
        try
        {
            var original = await GivenAcceptedPurchase(store, identity, orderId);
            var changed = field switch
            {
                "quantity" => identity with { Quantity = 9 },
                "provider" => identity with { Provider = "wiremock" },
                _ => identity with { ProductId = Guid.NewGuid() }
            };
            var error = await WhenCreatingChangedPurchase(store, supplier, changed);
            await ThenOriginalRemainsAndSupplierWasNotCalled(dataSource, store, supplier, original, error);
        }
        finally { await CleanupOwnRows(dataSource, identity.ClientRequestId); }
    }

    private static NpgsqlDataSource GivenDataSource() => NpgsqlDataSource.Create(
        Environment.GetEnvironmentVariable(ExternalIntegrationFactAttribute.ConnectionVariable)!);

    private static PurchaseIdentity GivenIdentity() =>
        new(Guid.NewGuid(), Guid.NewGuid(), "REAL-001", 10, 100m, "TWD", "direct");

    private static async Task GivenAdditiveSchema(NpgsqlDataSource dataSource)
    {
        var sql = await File.ReadAllTextAsync(Path.Combine(AppContext.BaseDirectory, "Schema", "procurement.sql"));
        await using var connection = await dataSource.OpenConnectionAsync();
        await using var command = new NpgsqlCommand(sql, connection);
        await command.ExecuteNonQueryAsync();
    }

    private static Task<CreateCommittedPurchase[]> WhenTwoCreatorsRace(PostgresPurchaseStore store,
        PurchaseIdentity identity, IReadOnlyList<Guid> ids) => Task.WhenAll(ids.Select(id =>
        store.CreateOrGetAsync(PurchaseOrder.Create(id, identity, DateTimeOffset.UtcNow), CancellationToken.None)));

    private static async Task ThenOnePurchaseWasCommitted(NpgsqlDataSource dataSource,
        PurchaseIdentity identity, IReadOnlyList<CreateCommittedPurchase> created)
    {
        Assert.Equal(2, created.Count);
        Assert.Single(created, result => result.Created);
        Assert.Single(created, result => !result.Created);
        Assert.Equal(created[0].Order.Id, created[1].Order.Id);
        Assert.Equal(identity, created[0].Order.Identity);
        await using var connection = await dataSource.OpenConnectionAsync();
        Assert.Equal(1, await connection.ExecuteScalarAsync<int>(
            "SELECT count(*) FROM procurement_purchase_orders WHERE client_request_id=@ClientRequestId",
            new { identity.ClientRequestId }));
    }

    private static async Task<PurchaseOrder> GivenAcceptedPurchase(PostgresPurchaseStore store,
        PurchaseIdentity identity, Guid orderId)
    {
        var created = await store.CreateOrGetAsync(PurchaseOrder.Create(orderId, identity, DateTimeOffset.UtcNow),
            CancellationToken.None);
        Assert.True(created.Created);
        return await store.ApplyOutcomeAsync(created.Order.Id,
            new SupplierOrderOutcome(true, "vendor-pg"), CancellationToken.None);
    }

    private static ValueTask<Exception?> WhenCreatingChangedPurchase(PostgresPurchaseStore store,
        ISupplierGateway supplier, PurchaseIdentity changed) => Record.ExceptionAsync(() =>
        new CreatePurchaseUseCase(store, store, supplier).ExecuteAsync(
            new CreatePurchaseInput(changed), CancellationToken.None));

    private static async Task ThenOriginalRemainsAndSupplierWasNotCalled(NpgsqlDataSource dataSource,
        PostgresPurchaseStore store, ISupplierGateway supplier, PurchaseOrder original, Exception? error)
    {
        Assert.Equal("purchase_identity_conflict", Assert.IsType<ProcurementRuleException>(error).Code);
        var persisted = await store.GetByIdAsync(original.Id, CancellationToken.None);
        Assert.NotNull(persisted);
        Assert.Equal(new PurchaseIdentityResponse(original.Identity.ClientRequestId, original.Identity.ProductId,
            original.Identity.SupplierSku, original.Identity.Quantity, original.Identity.UnitPrice,
            original.Identity.Currency, original.Identity.Provider), persisted.Identity);
        Assert.Equal(PurchaseOrderState.Accepted, persisted.State);
        Assert.Equal("vendor-pg", persisted.SupplierOrderId);
        await supplier.DidNotReceive().SubmitAsync(Arg.Any<PurchaseIdentity>(), Arg.Any<CancellationToken>());
        await using var connection = await dataSource.OpenConnectionAsync();
        Assert.Equal(1, await connection.ExecuteScalarAsync<int>(
            "SELECT count(*) FROM procurement_purchase_orders WHERE client_request_id=@ClientRequestId",
            new { original.Identity.ClientRequestId }));
    }

    private static async Task CleanupOwnRows(NpgsqlDataSource dataSource, Guid clientRequestId)
    {
        await using var connection = await dataSource.OpenConnectionAsync();
        await connection.ExecuteAsync("DELETE FROM procurement_purchase_orders WHERE client_request_id=@ClientRequestId",
            new { ClientRequestId = clientRequestId });
    }
}
