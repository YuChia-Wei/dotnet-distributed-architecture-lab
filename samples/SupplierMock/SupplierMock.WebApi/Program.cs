using System.Net;
using System.Net.Http.Json;
using System.Text.Json;
using WireMock.Server;
using WireMock.Settings;

var builder = WebApplication.CreateBuilder(args);
var modeValue = builder.Configuration["SupplierMock:Mode"] ?? "hybrid";
var upstreamValue = builder.Configuration["SupplierMock:UpstreamUrl"] ?? "http://supplier-sandbox:8080";
var nativeListenUrl = builder.Configuration["SupplierMock:NativeListenUrl"] ?? "http://0.0.0.0:9091";
var adminUrl = builder.Configuration["SupplierMock:AdminUrl"] ?? "http://127.0.0.1:9091";
var upstream = WireMockPresetController.ValidateUpstream(upstreamValue);
var initialMode = WireMockModeExtensions.Parse(modeValue);
var wireMock = WireMockServer.Start(new WireMockServerSettings { Urls = [nativeListenUrl], StartAdminInterface = true });
var adminClient = new HttpClient { BaseAddress = new Uri(adminUrl, UriKind.Absolute), Timeout = TimeSpan.FromSeconds(5) };
var controller = new WireMockPresetController(adminClient, upstream, initialMode);
await controller.ResetAsync(initialMode);
builder.Services.AddSingleton(controller);
builder.Services.AddSingleton(wireMock);
builder.Services.AddSingleton(adminClient);
var app = builder.Build();
app.Lifetime.ApplicationStopping.Register(wireMock.Stop);
app.Lifetime.ApplicationStopping.Register(adminClient.Dispose);

app.MapGet("/health", async (WireMockPresetController c, CancellationToken ct) => {
    var response = await c.GetNativeHealthAsync(ct);
    return response.IsSuccessStatusCode ? Results.Ok(new { status = "healthy" }) : Results.StatusCode(503);
});
app.MapGet("/control/state", (WireMockPresetController c) => Results.Ok(new { mode = c.Mode.ToString().ToLowerInvariant(), upstream = c.Upstream, persistence = "runtime setting; reset to configured startup mode when process restarts" }));
app.MapPost("/control/mode", async (ChangeModeRequest request, WireMockPresetController c, CancellationToken ct) => {
    if (!WireMockModeExtensions.TryParse(request.Mode, out var mode)) return Results.BadRequest(new { code = "invalid_mode", message = "Mode must be mock, proxy, or hybrid." });
    await c.ResetAsync(mode, ct);
    return Results.Ok(new { mode = c.Mode.ToString().ToLowerInvariant(), upstream = c.Upstream, persistence = "transient until process restart" });
});
app.MapPost("/control/reset", async (WireMockPresetController c, CancellationToken ct) => { await c.ResetAsync(c.StartupMode, ct); return Results.Ok(new { mode = c.Mode.ToString().ToLowerInvariant(), persistence = "reset to configured startup preset" }); });
app.MapGet("/control/mappings", async (WireMockPresetController c, CancellationToken ct) => Results.Content(await c.GetJsonAsync("__admin/mappings", ct), "application/json"));
app.MapGet("/control/requests", async (WireMockPresetController c, CancellationToken ct) => Results.Content(await c.GetJsonAsync("__admin/requests", ct), "application/json"));
app.MapDelete("/control/requests", async (WireMockPresetController c, CancellationToken ct) => { await c.ResetRequestsAsync(ct); return Results.NoContent(); });
app.MapGet("/", (WireMockPresetController c) => Results.Content(WireMockPage.Html.Replace("__MODE__", c.Mode.ToString().ToLowerInvariant(), StringComparison.Ordinal).Replace("__UPSTREAM__", WebUtility.HtmlEncode(c.Upstream), StringComparison.Ordinal), "text/html; charset=utf-8"));
app.Run();

public sealed record ChangeModeRequest(string Mode);
public sealed record WireMockPreset(string Mode, string MockSku, Guid FixtureClientRequestId, string FixtureSupplierOrderId, int Quantity, decimal UnitPrice);

public enum WireMockMode { Mock, Proxy, Hybrid }
public static class WireMockModeExtensions {
    public static WireMockMode Parse(string text) => TryParse(text, out var mode) ? mode : throw new InvalidOperationException("SupplierMock:Mode must be mock, proxy, or hybrid.");
    public static bool TryParse(string? text, out WireMockMode mode) => Enum.TryParse<WireMockMode>(text, true, out mode) && Enum.IsDefined(mode);
}

public sealed class WireMockPresetController(HttpClient admin, Uri upstream, WireMockMode startupMode) {
public string Upstream => upstream.ToString().TrimEnd('/');
    public WireMockMode Mode { get; private set; }
    public WireMockMode StartupMode { get; } = startupMode;

    public static Uri ValidateUpstream(string value) {
        if (!Uri.TryCreate(value, UriKind.Absolute, out var uri) || (uri.Scheme != Uri.UriSchemeHttp && uri.Scheme != Uri.UriSchemeHttps) || !string.IsNullOrEmpty(uri.UserInfo) || uri.Query.Length != 0 || uri.Fragment.Length != 0 || uri.AbsolutePath != "/")
            throw new InvalidOperationException("SupplierMock upstream must be an HTTP(S) origin with no credentials, path, query, or fragment.");
        if (uri.Host is not ("supplier-sandbox" or "localhost" or "127.0.0.1" or "::1"))
            throw new InvalidOperationException("SupplierMock upstream host must be supplier-sandbox or a loopback host.");
        return uri;
    }

    public async Task ResetAsync(WireMockMode mode, CancellationToken ct = default) {
        var preset = LoadPreset(mode);
        var quoteBody = new { sku = preset.MockSku, name = "WireMock fixture product", unitPrice = preset.UnitPrice, currency = "TWD", origin = "wiremock" };
        var orderBody = new { supplierOrderId = preset.FixtureSupplierOrderId, clientRequestId = preset.FixtureClientRequestId, sku = preset.MockSku, quantity = preset.Quantity, unitPrice = preset.UnitPrice, currency = "TWD", status = "accepted", origin = "wiremock" };
        await admin.DeleteAsync("__admin/mappings", ct);
        await admin.DeleteAsync("__admin/requests", ct);
        if (mode != WireMockMode.Proxy) {
            await AddMappingAsync(new {
                Priority = 1,
                Request = new { Methods = new[] { "get" }, Path = new { Matchers = new[] { new { Name = "WildcardMatcher", Pattern = $"/supplier/catalog/{preset.MockSku}" } } } },
                Response = new { StatusCode = 200, BodyAsJson = quoteBody, Headers = new Dictionary<string, string> { ["Content-Type"] = "application/json", ["X-Supplier-Origin"] = "wiremock" } }
            }, ct);
            await AddMappingAsync(new {
                Priority = 1,
                Request = new { Methods = new[] { "post" }, Path = new { Matchers = new[] { new { Name = "WildcardMatcher", Pattern = "/supplier/orders" } } }, Body = new { Matcher = new { Name = "JsonPartialMatcher", Pattern = JsonSerializer.Serialize(new { clientRequestId = preset.FixtureClientRequestId, sku = preset.MockSku }) } } },
                Response = new { StatusCode = 200, BodyAsJson = orderBody, Headers = new Dictionary<string, string> { ["Content-Type"] = "application/json", ["X-Supplier-Origin"] = "wiremock" } }
            }, ct);
            await AddMappingAsync(new {
                Priority = 1,
                Request = new { Methods = new[] { "get" }, Path = new { Matchers = new[] { new { Name = "WildcardMatcher", Pattern = $"/supplier/orders/by-client-request/{preset.FixtureClientRequestId}" } } } },
                Response = new { StatusCode = 200, BodyAsJson = orderBody, Headers = new Dictionary<string, string> { ["Content-Type"] = "application/json", ["X-Supplier-Origin"] = "wiremock" } }
            }, ct);
        }
        if (mode != WireMockMode.Mock) {
            await AddMappingAsync(new {
                Priority = 10,
                Request = new { Path = new { Matchers = new[] { new { Name = "WildcardMatcher", Pattern = "/*" } } } },
                Response = new { ProxyUrl = Upstream, UseTransformer = false }
            }, ct);
        }
        Mode = mode;
    }

    private static WireMockPreset LoadPreset(WireMockMode mode) {
        var path = Path.Combine(AppContext.BaseDirectory, "presets", mode.ToString().ToLowerInvariant() + ".json");
        var preset = JsonSerializer.Deserialize<WireMockPreset>(File.ReadAllText(path), new JsonSerializerOptions(JsonSerializerDefaults.Web));
        if (preset is null || preset.Mode != mode.ToString().ToLowerInvariant() || preset.FixtureClientRequestId == Guid.Empty || !IsValidFixtureSku(preset.MockSku) || string.IsNullOrWhiteSpace(preset.FixtureSupplierOrderId) || preset.Quantity <= 0 || preset.UnitPrice < 0) throw new InvalidOperationException($"Invalid WireMock preset: {path}");
        return preset;
    }
    private static bool IsValidFixtureSku(string sku) => System.Text.RegularExpressions.Regex.IsMatch(sku, "^[A-Za-z0-9_-]{1,64}$", System.Text.RegularExpressions.RegexOptions.CultureInvariant);
    public async Task<string> GetJsonAsync(string path, CancellationToken ct) => await admin.GetStringAsync(path, ct);
    public Task<HttpResponseMessage> GetNativeHealthAsync(CancellationToken ct) => admin.GetAsync("__admin/health", ct);
    public async Task ResetRequestsAsync(CancellationToken ct) { using var _ = await admin.DeleteAsync("__admin/requests", ct); }
    public void DisposeAdminClient() => admin.Dispose();
    private async Task AddMappingAsync(object mapping, CancellationToken ct) {
        using var response = await admin.PostAsJsonAsync("__admin/mappings", mapping, ct);
        response.EnsureSuccessStatusCode();
    }
}

public static class WireMockPage { public const string Html = """
<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>SupplierMock local lab UI</title><style>body{font:16px system-ui;max-width:1000px;margin:2rem auto;padding:0 1rem;color:#172033}button{padding:.55rem;margin:.2rem}section{border:1px solid #ccd4e0;border-radius:8px;padding:1rem;margin:1rem 0}pre{white-space:pre-wrap;background:#f2f5f9;padding:1rem;max-height:18rem;overflow:auto}.badge{background:#e5efff;padding:.3rem .6rem}</style></head><body><h1>SupplierMock.WebApi</h1><p><strong>Custom local lab controls</strong> for the genuine embedded WireMock.Net server. This is not a WireMock built-in dashboard or WireMockInspector.</p><p>Current mode: <span id="mode" class="badge">__MODE__</span> · Fixed upstream: <code id="upstream">__UPSTREAM__</code></p><p><button onclick="setWireMockMode('mock')">Mock</button><button onclick="setWireMockMode('proxy')">Proxy</button><button onclick="setWireMockMode('hybrid')">Hybrid</button><button onclick="resetPreset()">Reset startup preset</button><button onclick="refresh()">Refresh mappings and request journal</button><button onclick="clearRequests()">Clear journal</button></p><p>Mode controls affect native WireMock mappings and last until restart. Upstream is startup configuration only. Hybrid serves MOCK-001 fixtures at priority 1 and forwards other paths at priority 10.</p><p><a href="/control/mappings">Native mappings JSON</a> · <a href="/control/requests">Native request journal JSON</a> · <a href="http://localhost:8184">Microcks native UI</a> · <a href="http://localhost:8181">Supplier sandbox</a></p><section><h2>Actual native mappings</h2><pre id="mappings"></pre></section><section><h2>Actual native request journal</h2><pre id="requests"></pre></section><script>async function setWireMockMode(m){let r=await fetch('/control/mode',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({mode:m})});if(!r.ok)alert((await r.json()).message);refresh()}async function resetPreset(){await fetch('/control/reset',{method:'POST'});refresh()}async function clearRequests(){await fetch('/control/requests',{method:'DELETE'});refresh()}async function refresh(){let s=await(await fetch('/control/state')).json();document.getElementById("mode").textContent=s.mode;document.getElementById("upstream").textContent=s.upstream;for(let [p,i] of [['/control/mappings','mappings'],['/control/requests','requests']])document.getElementById(i).textContent=JSON.stringify(await(await fetch(p)).json(),null,2)}refresh();setInterval(refresh,5000)</script></body></html>
"""; }
public partial class Program { }
