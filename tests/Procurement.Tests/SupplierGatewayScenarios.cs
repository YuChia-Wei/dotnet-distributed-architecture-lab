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
    // P05 / AC01: identity mismatches from an HTTP provider are indeterminate, never accepted.
    [Fact, Trait("Scenario", "P05")]
    public async Task Mismatched_http_order_is_rejected_by_gateway()
    {
        var identity = GivenPurchaseIdentity();
        var gateway = GivenGatewayRespondsWithMismatchedIdentity(identity, out var sent);
        var error = await WhenSubmittingOrder(gateway, identity);
        ThenGatewayReportsInvalidResponse(error, sent, identity);
    }

    // AC03 adapter path: a configured service prefix survives relative route joining.
    [Fact, Trait("Scenario", "M04-adapter")]
    public async Task Microcks_profile_keeps_service_prefix_and_supplier_route()
    {
        var gateway = GivenGatewayReturnsQuote(out var sent);
        var quote = await WhenRequestingQuote(gateway);
        ThenQuoteUsesConfiguredPrefix(quote, sent);
    }

    private static PurchaseIdentity GivenPurchaseIdentity() =>
        new(Guid.NewGuid(), Guid.NewGuid(), "REAL-001", 10, 100m, "TWD", "direct");

    private static HttpSupplierGateway GivenGatewayRespondsWithMismatchedIdentity(PurchaseIdentity identity,
        out List<(Uri Uri, string Body)> sent)
    {
        sent = [];
        var observations = sent;
        var handler = new StubHandler(async request =>
        {
            observations.Add((request.RequestUri!, await request.Content!.ReadAsStringAsync()));
            var body = JsonSerializer.Serialize(new
            {
                supplierOrderId = "vendor-42", clientRequestId = identity.ClientRequestId,
                sku = identity.SupplierSku, quantity = 9, unitPrice = identity.UnitPrice,
                currency = identity.Currency, status = "accepted", origin = "sandbox"
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

    private static HttpSupplierGateway BuildGateway(string name, Uri baseAddress, HttpMessageHandler handler)
    {
        var factory = Substitute.For<IHttpClientFactory>();
        factory.CreateClient(name).Returns(new HttpClient(handler) { BaseAddress = baseAddress });
        return new HttpSupplierGateway(factory);
    }

    private static ValueTask<Exception?> WhenSubmittingOrder(HttpSupplierGateway gateway, PurchaseIdentity identity) =>
        Record.ExceptionAsync(() => gateway.SubmitAsync(identity, CancellationToken.None));
    private static Task<SupplierQuote> WhenRequestingQuote(HttpSupplierGateway gateway) =>
        gateway.QuoteAsync("microcks", "REAL-001", CancellationToken.None);

    private static void ThenGatewayReportsInvalidResponse(Exception? error,
        IReadOnlyList<(Uri Uri, string Body)> sent, PurchaseIdentity identity)
    {
        Assert.Equal("supplier_invalid_response", Assert.IsType<SupplierGatewayException>(error).Code);
        Assert.Single(sent);
        Assert.Equal("/supplier/orders", sent[0].Uri.AbsolutePath);
        using var body = JsonDocument.Parse(sent[0].Body);
        Assert.Equal(identity.ClientRequestId, body.RootElement.GetProperty("clientRequestId").GetGuid());
        Assert.Equal(10, body.RootElement.GetProperty("quantity").GetInt32());
    }
    private static void ThenQuoteUsesConfiguredPrefix(SupplierQuote quote, IReadOnlyList<Uri> sent)
    {
        Assert.Single(sent);
        Assert.Equal("/rest/Supplier/1.0/supplier/catalog/REAL-001", sent[0].AbsolutePath);
        Assert.Equal("sandbox", quote.Origin);
        Assert.Equal(100m, quote.UnitPrice);
    }

    private sealed class StubHandler(Func<HttpRequestMessage, Task<HttpResponseMessage>> send) : HttpMessageHandler
    {
        protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken) => send(request);
    }
}
