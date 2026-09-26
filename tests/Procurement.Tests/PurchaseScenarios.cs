using NSubstitute;
using Procurement.Applications;
using Procurement.Domains;

namespace Procurement.Tests;

public sealed class PurchaseScenarios
{
    private readonly PurchaseIdentity identity = new(Guid.NewGuid(), Guid.NewGuid(), "REAL-001", 10, 100m, "TWD", "direct");
    private readonly InMemoryCommitter store = new();
    private readonly ISupplierGateway supplier = Substitute.For<ISupplierGateway>();

    // P01 / AC01: the real use case persists the original key and records the verified provider outcome.
    [Fact, Trait("Scenario", "P01")]
    public async Task Accepted_purchase_uses_original_client_key()
    {
        GivenSupplierAccepts("vendor-42");
        var result = await WhenCreatingPurchase(identity);
        ThenPurchaseIsAccepted(result, "vendor-42");
        await ThenSupplierReceivedOriginalIdentity(identity);
    }

    // P02 / AC01: a completed matching replay cannot submit a second vendor order.
    [Fact, Trait("Scenario", "P02")]
    public async Task Matching_replay_returns_same_purchase_without_resubmission()
    {
        GivenSupplierAccepts("vendor-42");
        var first = await WhenCreatingPurchase(identity);
        var replay = await WhenCreatingPurchase(identity);
        ThenReplayUsesSameIdentity(first, replay);
        await ThenSupplierWasSubmittedOnce();
    }

    // P03 / AC01: one key is bound to all immutable fields, including provider and ProductId.
    [Theory, Trait("Scenario", "P03")]
    [InlineData("quantity")]
    [InlineData("provider")]
    [InlineData("product")]
    public async Task Changed_payload_conflicts_before_supplier_call(string field)
    {
        GivenSupplierAccepts("vendor-42");
        var first = await WhenCreatingPurchase(identity);
        var changed = field switch
        {
            "quantity" => identity with { Quantity = 9 },
            "provider" => identity with { Provider = "wiremock" },
            _ => identity with { ProductId = Guid.NewGuid() }
        };
        var error = await WhenCreatingConflictingPurchase(changed);
        ThenConflictPreservesOriginal(first, error);
        await ThenSupplierWasSubmittedOnce();
    }

    // P05 / AC01: an indeterminate response becomes durable unknown and never claims acceptance.
    [Fact, Trait("Scenario", "P05")]
    public async Task Malformed_provider_response_is_unknown()
    {
        GivenSupplierResponseIsInvalid();
        var result = await WhenCreatingPurchase(identity);
        ThenSubmissionIsUnknown(result);
    }

    // P06 / AC01: a rejected order cannot receive physical goods.
    [Fact, Trait("Scenario", "P06")]
    public async Task Rejected_purchase_forbids_receipt()
    {
        GivenSupplierRejects("denied-1");
        var created = await WhenCreatingPurchase(identity);
        var error = await WhenReceivingRejectedOrder(created.Order);
        ThenReceiptIsForbidden(error, created.Order);
    }

    // P07 / AC01: invalid payloads fail before either port is called.
    [Theory, Trait("Scenario", "P07")]
    [InlineData("guid")]
    [InlineData("sku")]
    [InlineData("quantity")]
    [InlineData("price")]
    [InlineData("currency")]
    public async Task Invalid_purchase_fails_before_io(string field)
    {
        var invalid = field switch
        {
            "guid" => identity with { ClientRequestId = Guid.Empty },
            "sku" => identity with { SupplierSku = "bad sku" },
            "quantity" => identity with { Quantity = 0 },
            "price" => identity with { UnitPrice = -1m },
            _ => identity with { Currency = "USD" }
        };
        var error = await WhenCreatingConflictingPurchase(invalid);
        await ThenInvalidInputHadNoEffects(error);
    }

    private void GivenSupplierAccepts(string vendorId) => supplier.SubmitAsync(Arg.Any<PurchaseIdentity>(), Arg.Any<CancellationToken>())
        .Returns(Task.FromResult(new SupplierOrderOutcome(true, vendorId)));
    private void GivenSupplierRejects(string vendorId) => supplier.SubmitAsync(Arg.Any<PurchaseIdentity>(), Arg.Any<CancellationToken>())
        .Returns(Task.FromResult(new SupplierOrderOutcome(false, vendorId)));
    private void GivenSupplierResponseIsInvalid() => supplier.SubmitAsync(Arg.Any<PurchaseIdentity>(), Arg.Any<CancellationToken>())
        .Returns(Task.FromException<SupplierOrderOutcome>(new SupplierGatewayException("supplier_invalid_response", "invalid")));

    private Task<CreatePurchaseResult> WhenCreatingPurchase(PurchaseIdentity input) =>
        new CreatePurchaseUseCase(store, store, supplier).ExecuteAsync(new CreatePurchase(input), CancellationToken.None);
    private ValueTask<Exception?> WhenCreatingConflictingPurchase(PurchaseIdentity input) =>
        Record.ExceptionAsync(() => WhenCreatingPurchase(input));
    private ValueTask<Exception?> WhenReceivingRejectedOrder(PurchaseOrder order) =>
        Record.ExceptionAsync(() => new ReceiveGoodsUseCase(store).ExecuteAsync(
            new ReceiveGoods(order.Id, Guid.NewGuid(), 1), CancellationToken.None));

    private static void ThenPurchaseIsAccepted(CreatePurchaseResult result, string vendorId)
    {
        Assert.True(result.Created);
        Assert.Equal(PurchaseOrderState.Accepted, result.Order.State);
        Assert.Equal(vendorId, result.Order.SupplierOrderId);
        Assert.Empty(result.Order.Receipts);
    }
    private async Task ThenSupplierReceivedOriginalIdentity(PurchaseIdentity expected) =>
        await supplier.Received(1).SubmitAsync(expected, Arg.Any<CancellationToken>());
    private static void ThenReplayUsesSameIdentity(CreatePurchaseResult first, CreatePurchaseResult replay)
    {
        Assert.False(replay.Created);
        Assert.Equal(first.Order.Id, replay.Order.Id);
        Assert.Equal(first.Order.SupplierOrderId, replay.Order.SupplierOrderId);
    }
    private async Task ThenSupplierWasSubmittedOnce() =>
        await supplier.Received(1).SubmitAsync(Arg.Any<PurchaseIdentity>(), Arg.Any<CancellationToken>());
    private static void ThenConflictPreservesOriginal(CreatePurchaseResult first, Exception? error)
    {
        Assert.Equal("purchase_identity_conflict", Assert.IsType<ProcurementRuleException>(error).Code);
        Assert.Equal(PurchaseOrderState.Accepted, first.Order.State);
    }
    private static void ThenSubmissionIsUnknown(CreatePurchaseResult result)
    {
        Assert.Equal(PurchaseOrderState.SubmissionUnknown, result.Order.State);
        Assert.Null(result.Order.SupplierOrderId);
        Assert.Empty(result.Order.Receipts);
    }
    private static void ThenReceiptIsForbidden(Exception? error, PurchaseOrder order)
    {
        Assert.Equal("receipt_state_conflict", Assert.IsType<ProcurementRuleException>(error).Code);
        Assert.Equal(0, order.ReceivedQuantity);
    }
    private async Task ThenInvalidInputHadNoEffects(Exception? error)
    {
        Assert.IsType<ProcurementRuleException>(error);
        Assert.Null(store.Current);
        await supplier.DidNotReceive().SubmitAsync(Arg.Any<PurchaseIdentity>(), Arg.Any<CancellationToken>());
    }

    private sealed class InMemoryCommitter : IPurchaseCreationCommitter, IPurchaseSubmissionCommitter, IGoodsReceiptCommitter
    {
        public PurchaseOrder? Current { get; private set; }
        public Task<CreatePurchaseResult> CreateOrGetAsync(PurchaseOrder candidate, CancellationToken cancellationToken)
        {
            if (Current is null) { Current = candidate; return Task.FromResult(new CreatePurchaseResult(candidate, true)); }
            return Task.FromResult(new CreatePurchaseResult(Current, false));
        }
        public Task<PurchaseOrder> ApplyOutcomeAsync(Guid id, SupplierOrderOutcome outcome, CancellationToken cancellationToken)
        {
            Current!.ApplySupplierOutcome(outcome.Accepted, outcome.SupplierOrderId, DateTimeOffset.UtcNow);
            return Task.FromResult(Current);
        }
        public Task<PurchaseOrder> MarkUnknownAsync(Guid id, CancellationToken cancellationToken)
        {
            Current!.MarkUnknown(DateTimeOffset.UtcNow);
            return Task.FromResult(Current);
        }
        public Task<ReceiveGoodsResult> CommitAsync(Guid purchaseOrderId, Guid receiptId,
            Func<PurchaseOrder, ReceiveGoodsResult> decide, CancellationToken cancellationToken) =>
            Task.FromResult(decide(Current!));
    }
}
