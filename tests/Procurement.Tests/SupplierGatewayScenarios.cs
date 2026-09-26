using System.Net;
using System.Text;
using System.Text.Json;
using NSubstitute;
using Procurement.Applications;
using Procurement.Domains;
using Procurement.Infrastructure;

namespace Procurement.Tests;

public sealed class SupplierGatewayScenarios
{
    // P05 / AC01 rows: actual HTTP adapter failure is portable and the real use case persists Unknown.
    [Theory, Trait("Scenario", "P05")]
    [InlineData("P05-5xx")]
    [InlineData("P05-malformed-json")]
    [InlineData("P05-unknown-status")]
    [InlineData("P05-identity-mismatch")]
    public async Task Invalid_http_result_never_claims_supplier_acceptance(string rowId)
    {
        var identity = GivenPurchaseIdentity();
        var gateway = GivenGatewayRespondsWith(rowId, identity, out var sent);
        var error = await WhenSubmittingOrder(gateway, identity);
        var store = new UnknownStore();
        var outcome = await WhenCreatingThroughUseCase(store, gateway, identity);
        ThenGatewayFailureIsPortableAndUnknown(rowId, error, outcome, store, sent, identity);
    }

    // AC03 adapter path: a configured service prefix survives relative route joining.
    [Fact, Trait("Scenario", "M04-adapter")]
    public async Task Microcks_profile_keeps_service_prefix_and_supplier_route()
    {
        var gateway = GivenGatewayReturnsQuote(out var sent);
        var quote = await WhenRequestingQuote(gateway);
        ThenQuoteUsesConfiguredPrefix(quote, sent);
    }

    // P05 transport rows: network and deadline failures are normalized at the HTTP adapter boundary.
    [Theory, Trait("Scenario", "P05-transport")]
    [InlineData("network", "supplier_unavailable")]
    [InlineData("timeout", "supplier_timeout")]
    public async Task Transport_failure_uses_portable_gateway_error(string failure, string expectedCode)
    {
        var identity = GivenPurchaseIdentity();
        var gateway = GivenGatewayThrowsTransportFailure(failure);
        var error = await WhenSubmittingOrder(gateway, identity);
        ThenTransportFailureIsPortable(error, expectedCode);
    }

    // Cancellation requested by the caller remains cancellation, while durable pending identity can be reconciled.
    [Fact, Trait("Scenario", "P05-cancellation")]
    public async Task Caller_cancellation_is_not_reported_as_provider_timeout()
    {
        var identity = GivenPurchaseIdentity();
        using var source = new CancellationTokenSource();
        source.Cancel();
        var gateway = GivenGatewayThrowsTransportFailure("timeout");
        var error = await WhenSubmittingWithCancellation(gateway, identity, source.Token);
        ThenCallerCancellationPropagates(error);
    }

    private static PurchaseIdentity GivenPurchaseIdentity() =>
        new(Guid.NewGuid(), Guid.NewGuid(), "REAL-001", 10, 100m, "TWD", "direct");

    private static HttpSupplierGateway GivenGatewayRespondsWith(string rowId, PurchaseIdentity identity,
        out List<(Uri Uri, string Body)> sent)
    {
        sent = [];
        var observations = sent;
        var handler = new StubHandler(async request =>
        {
            observations.Add((request.RequestUri!, await request.Content!.ReadAsStringAsync()));
            if (rowId == "P05-5xx") return new HttpResponseMessage(HttpStatusCode.ServiceUnavailable);
            if (rowId == "P05-malformed-json")
                return new HttpResponseMessage(HttpStatusCode.OK)
                {
                    Content = new StringContent("{broken-json", Encoding.UTF8, "application/json")
                };
            var body = JsonSerializer.Serialize(new
            {
                supplierOrderId = "vendor-42", clientRequestId = identity.ClientRequestId,
                sku = identity.SupplierSku,
                quantity = rowId == "P05-identity-mismatch" ? 9 : identity.Quantity,
                unitPrice = identity.UnitPrice,
                currency = identity.Currency,
                status = rowId == "P05-unknown-status" ? "pending" : "accepted",
                origin = "sandbox"
            });
            return new HttpResponseMessage(HttpStatusCode.OK) { Content = new StringContent(body, Encoding.UTF8, "application/json") };
        });
        return BuildGateway("supplier-direct", new Uri("http://supplier.local/"), handler);
    }

    private static HttpSupplierGateway GivenGatewayReturnsQuote(out List<Uri> sent)
    {
        sent = [];
        var observations = sent;
        var handler = new StubHandler(request =>
        {
            observations.Add(request.RequestUri!);
            return Task.FromResult(new HttpResponseMessage(HttpStatusCode.OK)
            {
                Content = new StringContent("""{"sku":"REAL-001","name":"Widget","unitPrice":100,"currency":"TWD","origin":"sandbox"}""",
                    Encoding.UTF8, "application/json")
            });
        });
        return BuildGateway("supplier-microcks", new Uri("http://microcks.local/rest/Supplier/1.0/"), handler);
    }

    private static HttpSupplierGateway GivenGatewayThrowsTransportFailure(string failure)
    {
        var handler = new StubHandler(_ => Task.FromException<HttpResponseMessage>(failure == "network"
            ? new HttpRequestException("connection failed") : new TaskCanceledException("deadline")));
        return BuildGateway("supplier-direct", new Uri("http://supplier.local/"), handler);
    }

    private static HttpSupplierGateway BuildGateway(string name, Uri baseAddress, HttpMessageHandler handler)
    {
        var factory = Substitute.For<IHttpClientFactory>();
        factory.CreateClient(name).Returns(new HttpClient(handler) { BaseAddress = baseAddress });
        return new HttpSupplierGateway(factory);
    }

    private static ValueTask<Exception?> WhenSubmittingOrder(HttpSupplierGateway gateway, PurchaseIdentity identity) =>
        Record.ExceptionAsync(() => gateway.SubmitAsync(identity, CancellationToken.None));
    private static ValueTask<Exception?> WhenSubmittingWithCancellation(HttpSupplierGateway gateway,
        PurchaseIdentity identity, CancellationToken cancellationToken) =>
        Record.ExceptionAsync(() => gateway.SubmitAsync(identity, cancellationToken));
    private static Task<CreatePurchaseOutput> WhenCreatingThroughUseCase(UnknownStore store,
        HttpSupplierGateway gateway, PurchaseIdentity identity) =>
        new CreatePurchaseUseCase(store, store, gateway).ExecuteAsync(new CreatePurchaseInput(identity), CancellationToken.None);
    private static Task<SupplierQuoteResponse> WhenRequestingQuote(HttpSupplierGateway gateway) =>
        gateway.QuoteAsync("microcks", "REAL-001", CancellationToken.None);

    private static void ThenGatewayFailureIsPortableAndUnknown(string rowId, Exception? error,
        CreatePurchaseOutput outcome, UnknownStore store, IReadOnlyList<(Uri Uri, string Body)> sent,
        PurchaseIdentity identity)
    {
        Assert.Equal(rowId == "P05-5xx" ? "supplier_unavailable" : "supplier_invalid_response",
            Assert.IsType<SupplierGatewayException>(error).Code);
        Assert.Equal(PurchaseOrderState.SubmissionUnknown, outcome.Order.State);
        Assert.Equal(PurchaseOrderState.SubmissionUnknown, store.Current!.State);
        Assert.Null(outcome.Order.SupplierOrderId);
        Assert.Equal(2, sent.Count); // Two explicit test actions; each use-case invocation sends once.
        Assert.Equal("/supplier/orders", sent[0].Uri.AbsolutePath);
        using var body = JsonDocument.Parse(sent[0].Body);
        Assert.Equal(identity.ClientRequestId, body.RootElement.GetProperty("clientRequestId").GetGuid());
        Assert.Equal(10, body.RootElement.GetProperty("quantity").GetInt32());
    }
    private static void ThenQuoteUsesConfiguredPrefix(SupplierQuoteResponse quote, IReadOnlyList<Uri> sent)
    {
        Assert.Single(sent);
        Assert.Equal("/rest/Supplier/1.0/supplier/catalog/REAL-001", sent[0].AbsolutePath);
        Assert.Equal("sandbox", quote.Origin);
        Assert.Equal(100m, quote.UnitPrice);
    }
    private static void ThenTransportFailureIsPortable(Exception? error, string expectedCode) =>
        Assert.Equal(expectedCode, Assert.IsType<SupplierGatewayException>(error).Code);
    private static void ThenCallerCancellationPropagates(Exception? error) =>
        Assert.IsAssignableFrom<OperationCanceledException>(error);

    private sealed class StubHandler(Func<HttpRequestMessage, Task<HttpResponseMessage>> send) : HttpMessageHandler
    {
        protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken) => send(request);
    }

    private sealed class UnknownStore : IPurchaseCreationCommitter, IPurchaseSubmissionCommitter
    {
        public PurchaseOrder? Current { get; private set; }
        public Task<CreateCommittedPurchase> CreateOrGetAsync(PurchaseOrder candidate, CancellationToken cancellationToken)
        {
            Current = candidate;
            return Task.FromResult(new CreateCommittedPurchase(candidate, true));
        }
        public Task<PurchaseOrder> ApplyOutcomeAsync(Guid id, SupplierOrderOutcome outcome, CancellationToken cancellationToken) =>
            throw new InvalidOperationException("Invalid responses must not be applied.");
        public Task<PurchaseOrder> MarkUnknownAsync(Guid id, CancellationToken cancellationToken)
        {
            Current!.MarkUnknown(DateTimeOffset.UtcNow);
            return Task.FromResult(Current);
        }
    }
}
