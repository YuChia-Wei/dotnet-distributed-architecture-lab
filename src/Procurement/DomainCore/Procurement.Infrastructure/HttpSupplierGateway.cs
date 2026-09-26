using System.Net;
using System.Net.Http.Json;
using System.Text.Json;
using Procurement.Applications;
using Procurement.Domains;

namespace Procurement.Infrastructure;

/// <summary>以固定命名路徑呼叫供應商，並將傳輸錯誤轉成應用層錯誤。</summary>
public sealed class HttpSupplierGateway(IHttpClientFactory clients) : ISupplierGateway
{
    private static readonly JsonSerializerOptions Json = new(JsonSerializerDefaults.Web);

    /// <inheritdoc />
    public Task<SupplierQuoteResponse> QuoteAsync(string provider, string sku, CancellationToken cancellationToken) =>
        NormalizeAsync(async () =>
    {
        new PurchaseIdentity(Guid.NewGuid(), Guid.NewGuid(), sku, 1, 0, "TWD", provider).Validate();
        using var response = await Client(provider).GetAsync($"supplier/catalog/{Uri.EscapeDataString(sku)}", cancellationToken);
        if (response.StatusCode == HttpStatusCode.NotFound)
            throw new SupplierGatewayException("supplier_not_found", "Supplier SKU was not found.");
        RequireSuccess(response);
        var body = await ReadAsync<QuoteBody>(response, cancellationToken);
        if (body is null || body.Sku != sku || body.Currency != "TWD" || body.UnitPrice < 0 ||
            string.IsNullOrWhiteSpace(body.Name) || string.IsNullOrWhiteSpace(body.Origin))
            throw new SupplierGatewayException("supplier_invalid_response", "Supplier quote response is invalid.");
        return new SupplierQuoteResponse(body.Sku, body.Name, body.UnitPrice, body.Currency, body.Origin);
    }, cancellationToken);

    /// <inheritdoc />
    public Task<SupplierOrderOutcome> SubmitAsync(PurchaseIdentity identity, CancellationToken cancellationToken) =>
        NormalizeAsync(async () =>
    {
        identity.Validate();
        using var response = await Client(identity.Provider).PostAsJsonAsync("supplier/orders", new
        {
            identity.ClientRequestId,
            Sku = identity.SupplierSku,
            identity.Quantity,
            identity.UnitPrice,
            identity.Currency
        }, Json, cancellationToken);
        if (response.StatusCode == HttpStatusCode.Conflict)
            throw new SupplierGatewayException("supplier_identity_conflict", "Supplier reports a client request identity conflict.");
        if (response.StatusCode == HttpStatusCode.BadRequest || response.StatusCode == HttpStatusCode.UnprocessableEntity)
            throw new SupplierGatewayException("supplier_business_rejection", "Supplier rejected the submitted purchase payload.");
        RequireSuccess(response);
        return ValidateOrder(await ReadAsync<OrderBody>(response, cancellationToken), identity);
    }, cancellationToken);

    /// <inheritdoc />
    public Task<SupplierLookup> LookupAsync(PurchaseIdentity identity, CancellationToken cancellationToken) =>
        NormalizeAsync(async () =>
    {
        using var response = await Client(identity.Provider).GetAsync(
            $"supplier/orders/by-client-request/{identity.ClientRequestId:D}", cancellationToken);
        if (response.StatusCode == HttpStatusCode.NotFound) return new SupplierLookup(SupplierLookupKind.NotFound);
        if (response.StatusCode == HttpStatusCode.Conflict)
            throw new SupplierGatewayException("supplier_identity_conflict", "Supplier reports a client request identity conflict.");
        RequireSuccess(response);
        return new SupplierLookup(SupplierLookupKind.Found,
            ValidateOrder(await ReadAsync<OrderBody>(response, cancellationToken), identity));
    }, cancellationToken);

    private static async Task<T> NormalizeAsync<T>(Func<Task<T>> call, CancellationToken cancellationToken)
    {
        try { return await call(); }
        catch (OperationCanceledException) when (cancellationToken.IsCancellationRequested) { throw; }
        catch (OperationCanceledException)
        {
            throw new SupplierGatewayException("supplier_timeout", "Supplier request timed out.");
        }
        catch (HttpRequestException)
        {
            throw new SupplierGatewayException("supplier_unavailable", "Supplier is unavailable.");
        }
    }

    private HttpClient Client(string provider) => provider switch
    {
        "direct" or "wiremock" or "microcks" => clients.CreateClient($"supplier-{provider}"),
        _ => throw new ProcurementRuleException("invalid_purchase", "Provider is invalid.")
    };

    private static void RequireSuccess(HttpResponseMessage response)
    {
        if (response.IsSuccessStatusCode) return;
        throw new SupplierGatewayException(response.StatusCode is HttpStatusCode.GatewayTimeout or HttpStatusCode.RequestTimeout
            ? "supplier_timeout" : "supplier_unavailable", "Supplier request did not complete successfully.");
    }

    private static async Task<T?> ReadAsync<T>(HttpResponseMessage response, CancellationToken cancellationToken)
    {
        try { return await response.Content.ReadFromJsonAsync<T>(Json, cancellationToken); }
        catch (JsonException) { throw new SupplierGatewayException("supplier_invalid_response", "Supplier response JSON is invalid."); }
    }

    private static SupplierOrderOutcome ValidateOrder(OrderBody? body, PurchaseIdentity identity)
    {
        if (body is null || body.ClientRequestId != identity.ClientRequestId ||
            body.Sku != identity.SupplierSku || body.Quantity != identity.Quantity ||
            body.UnitPrice != identity.UnitPrice || body.Currency != identity.Currency ||
            body.Status is not ("accepted" or "rejected") ||
            string.IsNullOrWhiteSpace(body.SupplierOrderId) || body.SupplierOrderId.Length > 128 ||
            string.IsNullOrWhiteSpace(body.Origin))
            throw new SupplierGatewayException("supplier_invalid_response", "Supplier order response does not match the purchase identity.");
        return new SupplierOrderOutcome(body.Status == "accepted", body.SupplierOrderId);
    }

    private sealed record QuoteBody(string Sku, string Name, decimal UnitPrice, string Currency, string Origin);
    private sealed record OrderBody(string SupplierOrderId, Guid ClientRequestId, string Sku,
        int Quantity, decimal UnitPrice, string Currency, string Status, string Origin);
}
