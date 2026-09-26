using System.Collections.Concurrent;
using System.Net;
using System.Net.Http.Json;
using System.Text;
using System.Text.Json;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Hosting.Server;
using Microsoft.AspNetCore.Hosting.Server.Features;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.DependencyInjection;
using WireMock.Server;

/// <summary>透過真實 HTTP 呼叫驗證 WireMock 模式與上游轉送行為。</summary>
public sealed class SupplierMockTests : IAsyncLifetime
{
    private WebApplication? upstream;
    private WireMockServer? wireMock;
    private WireMockPresetController? controller;
    private readonly HttpClient client = new();
    private readonly ConcurrentQueue<(string Path, string? Body)> forwarded = new();
    private const string FixtureId = "9d4c99da-6517-46b2-baa7-7e81106d3d34";

    /// <summary>依據固定範例、真實上游與目前模式驗證原生 HTTP 路由結果。</summary>
    [Fact]
    [Trait("Scenario", "M01-M02-M05-M06")]
    public async Task M01_M02_Given_a_real_local_upstream_When_modes_select_fixtures_proxy_or_mock_miss_Then_native_wiremock_forwards_only_the_selected_requests()
    {
        await GivenARealLocalUpstreamAsync();
        await GivenNativeWireMockWithHybridMappingsAsync();
        using var mockQuote = await WhenGetAsync("/supplier/catalog/MOCK-001");
        using var mockOrder = await WhenPostAsync("/supplier/orders", FixtureOrder());
        using var mockReconcile = await WhenGetAsync("/supplier/orders/by-client-request/" + FixtureId);
        using var realQuote = await WhenGetAsync("/supplier/catalog/REAL-001");
        var clientRequestId = Guid.NewGuid();
        var orderPayload = JsonSerializer.Serialize(new { clientRequestId, sku = "REAL-001", quantity = 4, unitPrice = 100m, currency = "TWD" });
        using var realOrder = await WhenPostAsync("/supplier/orders?trace=fixture", orderPayload);
        using var reconciled = await WhenGetAsync("/supplier/orders/by-client-request/" + clientRequestId);
        await ThenHybridSeparatesFixturesAndProxyAsync(mockQuote, mockOrder, mockReconcile, realQuote, realOrder, reconciled, clientRequestId, orderPayload);

        await WhenSwitchingToProxyModeAsync();
        using var proxyOnly = await WhenGetAsync("/supplier/catalog/MOCK-001");
        ThenProxyModeReachesUpstream(proxyOnly);

        await WhenSwitchingToMockModeAsync();
        using var mockOnlyMiss = await WhenGetAsync("/supplier/catalog/REAL-001");
        ThenMockModeMissDoesNotReachUpstream(mockOnlyMiss);
    }

    /// <summary>並行重設完成後，模式狀態、原生映射與實際回應必須一致。</summary>
    [Fact]
    [Trait("Scenario", "M07")]
    public async Task M07_Given_concurrent_mode_resets_When_native_http_is_used_Then_selected_mode_matches_a_complete_mapping_set()
    {
        await GivenARealLocalUpstreamAsync();
        await GivenNativeWireMockWithHybridMappingsAsync();

        var modes = Enumerable.Range(0, 18)
            .Select(index => (WireMockMode)(index % Enum.GetValues<WireMockMode>().Length))
            .ToArray();
        await Task.WhenAll(modes.Select(mode => controller!.ResetAsync(mode)));

        using var mappingsDocument = JsonDocument.Parse(
            await controller!.GetJsonAsync("__admin/mappings", CancellationToken.None));
        var mappings = mappingsDocument.RootElement.EnumerateArray().ToArray();
        var modeAfterResets = controller.Mode;
        var mockCount = mappings.Count(mapping => GetPriority(mapping) == 1);
        var proxyCount = mappings.Count(mapping => GetPriority(mapping) == 10);

        switch (modeAfterResets)
        {
            case WireMockMode.Mock:
                Assert.Equal(3, mockCount);
                Assert.Equal(0, proxyCount);
                Assert.Equal(3, mappings.Length);
                break;
            case WireMockMode.Proxy:
                Assert.Equal(0, mockCount);
                Assert.Equal(1, proxyCount);
                Assert.Single(mappings);
                break;
            case WireMockMode.Hybrid:
                Assert.Equal(3, mockCount);
                Assert.Equal(1, proxyCount);
                Assert.Equal(4, mappings.Length);
                break;
            default:
                throw new Xunit.Sdk.XunitException($"Unexpected final mode: {modeAfterResets}");
        }

        using var quoteResponse = await WhenGetAsync("/supplier/catalog/MOCK-001");
        Assert.Equal(HttpStatusCode.OK, quoteResponse.StatusCode);
        var expectedOrigin = modeAfterResets == WireMockMode.Proxy ? "sandbox" : "wiremock";
        Assert.Equal(expectedOrigin, quoteResponse.Headers.GetValues("X-Supplier-Origin").Single());
    }

    private static int GetPriority(JsonElement mapping)
    {
        if (mapping.TryGetProperty("priority", out var priority)
            || mapping.TryGetProperty("Priority", out priority))
        {
            return priority.GetInt32();
        }

        throw new Xunit.Sdk.XunitException(
            $"WireMock mapping did not expose a priority. Properties: {string.Join(", ", mapping.EnumerateObject().Select(property => property.Name))}");
    }

    private async Task GivenARealLocalUpstreamAsync()
    {
        var builder = WebApplication.CreateBuilder();
        builder.WebHost.UseUrls("http://127.0.0.1:0");
        upstream = builder.Build();
        upstream.MapGet("/supplier/catalog/{sku}", (string sku, HttpContext context) =>
        {
            forwarded.Enqueue(($"/supplier/catalog/{sku}", null));
            context.Response.Headers["X-Supplier-Origin"] = "sandbox";
            return Results.Json(new { sku, name = "Real local supplier", unitPrice = 100m, currency = "TWD", origin = "sandbox" });
        });
        upstream.MapPost("/supplier/orders", async (HttpRequest request, HttpContext context) =>
        {
            using var reader = new StreamReader(request.Body);
            var body = await reader.ReadToEndAsync();
            forwarded.Enqueue((request.Path + request.QueryString, body));
            using var doc = JsonDocument.Parse(body);
            var root = doc.RootElement;
            var id = root.GetProperty("clientRequestId").GetGuid();
            var sku = root.GetProperty("sku").GetString();
            var quantity = root.GetProperty("quantity").GetInt32();
            var price = root.GetProperty("unitPrice").GetDecimal();
            var currency = root.GetProperty("currency").GetString();
            context.Response.Headers["X-Supplier-Origin"] = "sandbox";
            return Results.Json(new { supplierOrderId = "real-order-" + id, clientRequestId = id, sku, quantity, unitPrice = price, currency, status = "accepted", origin = "sandbox" });
        });
        upstream.MapGet("/supplier/orders/by-client-request/{id:guid}", (Guid id, HttpContext context) =>
        {
            forwarded.Enqueue(($"/supplier/orders/by-client-request/{id}", null));
            context.Response.Headers["X-Supplier-Origin"] = "sandbox";
            return Results.Json(new { supplierOrderId = "real-order-" + id, clientRequestId = id, sku = "REAL-001", quantity = 4, unitPrice = 100m, currency = "TWD", status = "accepted", origin = "sandbox" });
        });
        await upstream.StartAsync();
    }

    private async Task GivenNativeWireMockWithHybridMappingsAsync()
    {
        var address = upstream!.Services.GetRequiredService<IServer>().Features.Get<IServerAddressesFeature>()!.Addresses.Single();
        wireMock = WireMockServer.StartWithAdminInterface();
        var admin = new HttpClient { BaseAddress = new Uri(wireMock.Url!) };
        controller = new WireMockPresetController(admin, WireMockPresetController.ValidateUpstream(address), WireMockMode.Hybrid);
        await controller.ResetAsync(WireMockMode.Hybrid);
    }

    private Task<HttpResponseMessage> WhenGetAsync(string path) => client.GetAsync(new Uri(wireMock!.Url + path));
    private Task<HttpResponseMessage> WhenPostAsync(string path, string body) => client.PostAsync(new Uri(wireMock!.Url + path), new StringContent(body, Encoding.UTF8, "application/json"));
    private Task WhenSwitchingToProxyModeAsync() => controller!.ResetAsync(WireMockMode.Proxy);
    private Task WhenSwitchingToMockModeAsync() => controller!.ResetAsync(WireMockMode.Mock);

    private static string FixtureOrder() => JsonSerializer.Serialize(new { clientRequestId = Guid.Parse(FixtureId), sku = "MOCK-001", quantity = 2, unitPrice = 100m, currency = "TWD" });

    private async Task ThenHybridSeparatesFixturesAndProxyAsync(HttpResponseMessage mockQuote, HttpResponseMessage mockOrder, HttpResponseMessage mockReconcile, HttpResponseMessage realQuote, HttpResponseMessage realOrder, HttpResponseMessage reconciled, Guid id, string requestBody)
    {
        Assert.Equal(HttpStatusCode.OK, mockQuote.StatusCode);
        Assert.Equal("wiremock", mockQuote.Headers.GetValues("X-Supplier-Origin").Single());
        Assert.Equal(HttpStatusCode.OK, mockOrder.StatusCode);
        Assert.Equal("wiremock", mockOrder.Headers.GetValues("X-Supplier-Origin").Single());
        using var mockBody = JsonDocument.Parse(await mockOrder.Content.ReadAsStringAsync());
        Assert.Equal(FixtureId, mockBody.RootElement.GetProperty("clientRequestId").GetString());
        Assert.Equal(HttpStatusCode.OK, mockReconcile.StatusCode);
        Assert.Equal("wiremock", mockReconcile.Headers.GetValues("X-Supplier-Origin").Single());

        Assert.Equal(HttpStatusCode.OK, realQuote.StatusCode);
        Assert.Equal("sandbox", realQuote.Headers.GetValues("X-Supplier-Origin").Single());
        Assert.Equal(HttpStatusCode.OK, realOrder.StatusCode);
        Assert.Equal("sandbox", realOrder.Headers.GetValues("X-Supplier-Origin").Single());
        using var realBody = JsonDocument.Parse(await realOrder.Content.ReadAsStringAsync());
        Assert.Equal(id, realBody.RootElement.GetProperty("clientRequestId").GetGuid());
        Assert.Equal(HttpStatusCode.OK, reconciled.StatusCode);
        Assert.Equal("sandbox", reconciled.Headers.GetValues("X-Supplier-Origin").Single());
        Assert.Equal(3, forwarded.Count);
        Assert.Contains("/supplier/orders?trace=fixture", forwarded.ElementAt(1).Path);
        Assert.Equal(requestBody, forwarded.ElementAt(1).Body);
    }

    private void ThenProxyModeReachesUpstream(HttpResponseMessage response)
    {
        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        Assert.Equal("sandbox", response.Headers.GetValues("X-Supplier-Origin").Single());
        Assert.Equal(4, forwarded.Count);
    }

    private void ThenMockModeMissDoesNotReachUpstream(HttpResponseMessage response)
    {
        Assert.NotEqual(HttpStatusCode.OK, response.StatusCode);
        Assert.Equal(4, forwarded.Count);
    }

    /// <summary>準備測試執行環境。</summary>
    public ValueTask InitializeAsync() => ValueTask.CompletedTask;

    /// <summary>釋放 HTTP 用戶端與本機供應商伺服器。</summary>
    /// <returns>非同步清理作業。</returns>
    public async ValueTask DisposeAsync()
    {
        controller?.DisposeAdminClient();
        client.Dispose();
        wireMock?.Stop();
        if (upstream is not null) await upstream.DisposeAsync();
    }
}
