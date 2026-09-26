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
var wireMock = WireMockServer.Start(new WireMockServerSettings
{
    Urls = [nativeListenUrl],
    StartAdminInterface = true
});
var adminClient = new HttpClient
{
    BaseAddress = new Uri(adminUrl, UriKind.Absolute),
    Timeout = TimeSpan.FromSeconds(5)
};
var controller = new WireMockPresetController(adminClient, upstream, initialMode);
await controller.ResetAsync(initialMode);
var microcksUrl = MicrocksPresetController.ValidateMicrocksOrigin(
    builder.Configuration["SupplierMock:MicrocksUrl"] ?? "http://microcks:8080");
var microcksClient = new HttpClient { BaseAddress = microcksUrl, Timeout = TimeSpan.FromSeconds(35) };
var microcksController = new MicrocksPresetController(microcksClient, Path.Combine(AppContext.BaseDirectory, "microcks"));

builder.Services.AddSingleton(controller);
builder.Services.AddSingleton(microcksController);
builder.Services.AddSingleton(wireMock);
builder.Services.AddSingleton(adminClient);

var app = builder.Build();
app.Lifetime.ApplicationStopping.Register(wireMock.Stop);
app.Lifetime.ApplicationStopping.Register(controller.DisposeAdminClient);
app.Lifetime.ApplicationStopping.Register(microcksClient.Dispose);

app.MapGet("/control/microcks/state", async (MicrocksPresetController presetController, CancellationToken cancellationToken) =>
    Results.Ok(await presetController.GetStateAsync(cancellationToken)));

app.MapPost("/control/microcks/mode", async (
    ChangeModeRequest request, MicrocksPresetController presetController, CancellationToken cancellationToken) =>
{
    if (!MicrocksPresetController.IsValidMode(request.Mode))
        return Results.BadRequest(new { code = "invalid_mode", message = "模式必須是 mock、proxy 或 hybrid。" });

    try
    {
        return Results.Ok(await presetController.ChangeAsync(request.Mode, cancellationToken));
    }
    catch (OperationCanceledException) when (cancellationToken.IsCancellationRequested)
    {
        return Results.StatusCode(499);
    }
    catch (Exception ex) when (ex is HttpRequestException or OperationCanceledException or InvalidDataException or IOException)
    {
        var state = await presetController.GetStateAsync();
        return Results.Json(state with { Mode = null, Status = state.Status == "unavailable" ? "unavailable" : "failed",
            Message = "Microcks 匯入或原生狀態確認失敗；請檢查服務並明確重試。" },
            statusCode: state.Status == "unavailable" ? 503 : 502);
    }
});

app.MapGet("/health", async (WireMockPresetController presetController, CancellationToken cancellationToken) =>
{
    var isHealthy = await presetController.IsNativeHealthyAsync(cancellationToken);
    return isHealthy ? Results.Ok(new { status = "healthy" }) : Results.StatusCode(503);
});

app.MapGet("/control/state", (WireMockPresetController presetController) => Results.Ok(new
{
    mode = presetController.Mode?.ToString().ToLowerInvariant(),
    status = presetController.Status,
    upstream = presetController.Upstream,
    persistence = "執行階段設定；重新啟動後回到啟動模式"
}));

app.MapPost("/control/mode", async (
    ChangeModeRequest request,
    WireMockPresetController presetController,
    CancellationToken cancellationToken) =>
{
    if (!WireMockModeExtensions.TryParse(request.Mode, out var mode))
    {
        return Results.BadRequest(new
        {
            code = "invalid_mode",
            message = "模式必須是 mock、proxy 或 hybrid。"
        });
    }

    await presetController.ResetAsync(mode, cancellationToken);
    return Results.Ok(new
    {
        mode = presetController.Mode?.ToString().ToLowerInvariant(),
        status = presetController.Status,
        upstream = presetController.Upstream,
        persistence = "設定只保留至服務重新啟動"
    });
});

app.MapPost("/control/reset", async (
    WireMockPresetController presetController,
    CancellationToken cancellationToken) =>
{
    await presetController.ResetAsync(presetController.StartupMode, cancellationToken);
    return Results.Ok(new
    {
        mode = presetController.Mode?.ToString().ToLowerInvariant(),
        status = presetController.Status,
        persistence = "已還原為啟動時的預設模式"
    });
});

app.MapGet("/control/mappings", async (
    WireMockPresetController presetController,
    CancellationToken cancellationToken) =>
    Results.Content(await presetController.GetJsonAsync("__admin/mappings", cancellationToken), "application/json"));

app.MapGet("/control/requests", async (
    WireMockPresetController presetController,
    CancellationToken cancellationToken) =>
    Results.Content(await presetController.GetJsonAsync("__admin/requests", cancellationToken), "application/json"));

app.MapDelete("/control/requests", async (
    WireMockPresetController presetController,
    CancellationToken cancellationToken) =>
{
    await presetController.ResetRequestsAsync(cancellationToken);
    return Results.NoContent();
});

app.MapGet("/", (WireMockPresetController presetController) => Results.Content(
    WireMockPage.Html
        .Replace("__MODE__", presetController.Mode?.ToString().ToLowerInvariant() ?? "unavailable", StringComparison.Ordinal)
        .Replace("__UPSTREAM__", WebUtility.HtmlEncode(presetController.Upstream), StringComparison.Ordinal)
        .Replace("__STATUS__", presetController.Status, StringComparison.Ordinal),
    "text/html; charset=utf-8"));

app.Run();

/// <summary>代表切換供應商模擬模式的請求。</summary>
/// <param name="Mode">要啟用的模式名稱：mock、proxy 或 hybrid。</param>
public sealed record ChangeModeRequest(string Mode);

/// <summary>描述可重設的 WireMock 預設資料。</summary>
/// <param name="Mode">預設所屬模式。</param>
/// <param name="MockSku">固定回傳報價的供應商 SKU。</param>
/// <param name="FixtureClientRequestId">固定訂單的用戶端請求識別碼。</param>
/// <param name="FixtureSupplierOrderId">固定供應商訂單識別碼。</param>
/// <param name="Quantity">固定訂單數量。</param>
/// <param name="UnitPrice">固定商品單價。</param>
public sealed record WireMockPreset(
    string Mode,
    string MockSku,
    Guid FixtureClientRequestId,
    string FixtureSupplierOrderId,
    int Quantity,
    decimal UnitPrice);

/// <summary>供應商模擬器支援的代理模式。</summary>
public enum WireMockMode
{
    /// <summary>只回傳本機固定範例。</summary>
    Mock,

    /// <summary>將所有供應商請求轉送至固定上游。</summary>
    Proxy,

    /// <summary>固定範例優先，其餘請求轉送至固定上游。</summary>
    Hybrid
}

/// <summary>提供供應商模擬模式的解析方法。</summary>
public static class WireMockModeExtensions
{
    /// <summary>解析設定中的模式名稱；不支援的值會擲出例外。</summary>
    /// <param name="text">設定檔中的模式名稱。</param>
    /// <returns>對應的供應商模擬模式。</returns>
    public static WireMockMode Parse(string text) => TryParse(text, out var mode)
        ? mode
        : throw new InvalidOperationException("SupplierMock:Mode 必須是 mock、proxy 或 hybrid。");

    /// <summary>嘗試解析模式名稱，不支援時回傳 false。</summary>
    /// <param name="text">要解析的模式名稱。</param>
    /// <param name="mode">解析成功時的模式。</param>
    /// <returns>名稱是否有效。</returns>
    public static bool TryParse(string? text, out WireMockMode mode)
    {
        mode = default;
        if (text is null)
        {
            return false;
        }

        foreach (var candidate in Enum.GetValues<WireMockMode>())
        {
            if (candidate.ToString().Equals(text, StringComparison.OrdinalIgnoreCase))
            {
                mode = candidate;
                return true;
            }
        }

        return false;
    }
}

/// <summary>透過 WireMock 管理 API 套用預設映射並回報目前設定。</summary>
/// <param name="admin">連至內部 WireMock 管理 API 的用戶端。</param>
/// <param name="upstream">固定且已驗證的供應商上游網址。</param>
/// <param name="startupMode">服務啟動時使用的模式。</param>
public sealed class WireMockPresetController(HttpClient admin, Uri upstream, WireMockMode startupMode)
{
    private readonly SemaphoreSlim resetGate = new(1, 1);

    /// <summary>取得固定上游的來源網址。</summary>
    public string Upstream => upstream.ToString().TrimEnd('/');

    /// <summary>取得最近一次完整套用的模式；正在套用或失敗時為 null。</summary>
    public WireMockMode? Mode { get; private set; }

    /// <summary>取得映射套用狀態：applying、ready 或 failed。</summary>
    public string Status { get; private set; } = "applying";

    /// <summary>取得服務啟動時設定的預設模式。</summary>
    public WireMockMode StartupMode { get; } = startupMode;

    /// <summary>驗證上游是允許的 HTTP(S) 來源網址。</summary>
    /// <param name="value">設定中的上游網址。</param>
    /// <returns>已驗證的絕對網址。</returns>
    /// <exception cref="InvalidOperationException">網址包含路徑、認證資訊，或主機不在允許清單中。</exception>
    public static Uri ValidateUpstream(string value)
    {
        if (!Uri.TryCreate(value, UriKind.Absolute, out var uri)
            || (uri.Scheme != Uri.UriSchemeHttp && uri.Scheme != Uri.UriSchemeHttps)
            || !string.IsNullOrEmpty(uri.UserInfo)
            || uri.Query.Length != 0
            || uri.Fragment.Length != 0
            || uri.AbsolutePath != "/")
        {
            throw new InvalidOperationException("SupplierMock 上游必須是沒有認證資訊、路徑、查詢或片段的 HTTP(S) 來源網址。");
        }

        if (uri.Host is not ("supplier-sandbox" or "localhost" or "127.0.0.1" or "::1"))
        {
            throw new InvalidOperationException("SupplierMock 上游主機必須是 supplier-sandbox 或本機迴路主機。");
        }

        return uri;
    }

    /// <summary>序列化重設操作，清除舊狀態並套用所選模式的完整映射。</summary>
    /// <param name="mode">要套用的供應商模擬模式。</param>
    /// <param name="ct">取消操作的權杖。</param>
    public async Task ResetAsync(WireMockMode mode, CancellationToken ct = default)
    {
        await resetGate.WaitAsync(ct);
        try
        {
            ct.ThrowIfCancellationRequested();
            var preset = LoadPreset(mode);
            ct.ThrowIfCancellationRequested();

            Status = "applying";
            Mode = null;
            try
            {
                using var operationTimeout = new CancellationTokenSource(TimeSpan.FromSeconds(30));
                await ResetCoreAsync(mode, preset, operationTimeout.Token);
                Mode = mode;
                Status = "ready";
            }
            catch
            {
                Mode = null;
                Status = "failed";
                throw;
            }
        }
        finally
        {
            resetGate.Release();
        }
    }

    private async Task ResetCoreAsync(WireMockMode mode, WireMockPreset preset, CancellationToken ct)
    {
        var quoteBody = new
        {
            sku = preset.MockSku,
            name = "WireMock 範例商品",
            unitPrice = preset.UnitPrice,
            currency = "TWD",
            origin = "wiremock"
        };
        var orderBody = new
        {
            supplierOrderId = preset.FixtureSupplierOrderId,
            clientRequestId = preset.FixtureClientRequestId,
            sku = preset.MockSku,
            quantity = preset.Quantity,
            unitPrice = preset.UnitPrice,
            currency = "TWD",
            status = "accepted",
            origin = "wiremock"
        };

        await DeleteAsync("__admin/mappings", ct);
        await DeleteAsync("__admin/requests", ct);

        if (mode != WireMockMode.Proxy)
        {
            await AddMappingAsync(new
            {
                Priority = 1,
                Request = new
                {
                    Methods = new[] { "get" },
                    Path = new
                    {
                        Matchers = new[]
                        {
                            new { Name = "WildcardMatcher", Pattern = $"/supplier/catalog/{preset.MockSku}" }
                        }
                    }
                },
                Response = new
                {
                    StatusCode = 200,
                    BodyAsJson = quoteBody,
                    Headers = new Dictionary<string, string>
                    {
                        ["Content-Type"] = "application/json",
                        ["X-Supplier-Origin"] = "wiremock"
                    }
                }
            }, ct);

            await AddMappingAsync(new
            {
                Priority = 1,
                Request = new
                {
                    Methods = new[] { "post" },
                    Path = new
                    {
                        Matchers = new[]
                        {
                            new { Name = "WildcardMatcher", Pattern = "/supplier/orders" }
                        }
                    },
                    Body = new
                    {
                        Matcher = new
                        {
                            Name = "JmesPathMatcher",
                            Pattern = "clientRequestId == '"
                                + preset.FixtureClientRequestId.ToString("D")
                                + "' && sku == '"
                                + preset.MockSku
                                + "' && quantity == `"
                                + preset.Quantity.ToString(System.Globalization.CultureInfo.InvariantCulture)
                                + "` && unitPrice >= `"
                                + preset.UnitPrice.ToString("G29", System.Globalization.CultureInfo.InvariantCulture)
                                + "` && unitPrice <= `"
                                + preset.UnitPrice.ToString("G29", System.Globalization.CultureInfo.InvariantCulture)
                                + "` && currency == 'TWD'"
                        }
                    }
                },
                Response = new
                {
                    StatusCode = 200,
                    BodyAsJson = orderBody,
                    Headers = new Dictionary<string, string>
                    {
                        ["Content-Type"] = "application/json",
                        ["X-Supplier-Origin"] = "wiremock"
                    }
                }
            }, ct);

            await AddMappingAsync(new
            {
                Priority = 1,
                Request = new
                {
                    Methods = new[] { "get" },
                    Path = new
                    {
                        Matchers = new[]
                        {
                            new
                            {
                                Name = "WildcardMatcher",
                                Pattern = $"/supplier/orders/by-client-request/{preset.FixtureClientRequestId}"
                            }
                        }
                    }
                },
                Response = new
                {
                    StatusCode = 200,
                    BodyAsJson = orderBody,
                    Headers = new Dictionary<string, string>
                    {
                        ["Content-Type"] = "application/json",
                        ["X-Supplier-Origin"] = "wiremock"
                    }
                }
            }, ct);
        }

        if (mode != WireMockMode.Mock)
        {
            await AddMappingAsync(new
            {
                Priority = 10,
                Request = new
                {
                    Path = new
                    {
                        Matchers = new[]
                        {
                            new { Name = "WildcardMatcher", Pattern = "/*" }
                        }
                    }
                },
                Response = new { ProxyUrl = Upstream, UseTransformer = false }
            }, ct);
        }

    }

    /// <summary>讀取 WireMock 原生管理 API 回傳的 JSON。</summary>
    /// <param name="path">相對於管理 API 的路徑。</param>
    /// <param name="ct">取消操作的權杖。</param>
    /// <returns>管理 API 的 JSON 文字。</returns>
    public async Task<string> GetJsonAsync(string path, CancellationToken ct) => await admin.GetStringAsync(path, ct);

    /// <summary>查詢 WireMock 原生伺服器是否正常運作。</summary>
    /// <param name="ct">取消操作的權杖。</param>
    /// <returns>原生管理 API 是否回報成功。</returns>
    public async Task<bool> IsNativeHealthyAsync(CancellationToken ct)
    {
        if (Status != "ready" || Mode is null)
        {
            return false;
        }

        using var response = await admin.GetAsync("__admin/health", ct);
        return response.IsSuccessStatusCode;
    }

    /// <summary>清除 WireMock 原生請求紀錄並確認管理 API 成功。</summary>
    /// <param name="ct">取消操作的權杖。</param>
    public async Task ResetRequestsAsync(CancellationToken ct) => await DeleteAsync("__admin/requests", ct);

    /// <summary>釋放管理 API 用戶端與重設同步閘門。</summary>
    public void DisposeAdminClient()
    {
        admin.Dispose();
        resetGate.Dispose();
    }

    private async Task DeleteAsync(string path, CancellationToken ct)
    {
        using var response = await admin.DeleteAsync(path, ct);
        response.EnsureSuccessStatusCode();
    }

    private static WireMockPreset LoadPreset(WireMockMode mode)
    {
        var path = Path.Combine(AppContext.BaseDirectory, "presets", mode.ToString().ToLowerInvariant() + ".json");
        var preset = JsonSerializer.Deserialize<WireMockPreset>(
            File.ReadAllText(path),
            new JsonSerializerOptions(JsonSerializerDefaults.Web));

        if (preset is null
            || preset.Mode != mode.ToString().ToLowerInvariant()
            || preset.FixtureClientRequestId == Guid.Empty
            || !IsValidFixtureSku(preset.MockSku)
            || string.IsNullOrWhiteSpace(preset.FixtureSupplierOrderId)
            || preset.Quantity <= 0
            || preset.UnitPrice < 0)
        {
            throw new InvalidOperationException($"WireMock 預設資料無效：{path}");
        }

        return preset;
    }

    private static bool IsValidFixtureSku(string sku) =>
        System.Text.RegularExpressions.Regex.IsMatch(
            sku,
            "^[A-Za-z0-9_-]{1,64}$",
            System.Text.RegularExpressions.RegexOptions.CultureInvariant);

    private async Task AddMappingAsync(object mapping, CancellationToken ct)
    {
        using var response = await admin.PostAsJsonAsync("__admin/mappings", mapping, ct);
        response.EnsureSuccessStatusCode();
    }
}

/// <summary>提供供操作人員檢視 WireMock 狀態的繁體中文頁面。</summary>
public static class WireMockPage
{
    /// <summary>本機供應商模擬器操作頁面的 HTML。</summary>
    public const string Html = """
        <!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>供應商模擬器</title><style>body{font:16px system-ui;max-width:1000px;margin:2rem auto;padding:0 1rem;color:#172033}button{padding:.55rem;margin:.2rem}section{border:1px solid #ccd4e0;border-radius:8px;padding:1rem;margin:1rem 0}pre{white-space:pre-wrap;background:#f2f5f9;padding:1rem;max-height:18rem;overflow:auto}.badge{background:#e5efff;padding:.3rem .6rem}</style></head><body><h1>SupplierMock.WebApi 供應商模擬器</h1><p><strong>本機實驗室操作介面</strong>，控制內嵌的 WireMock.Net 伺服器；這不是 WireMock 內建儀表板或 WireMockInspector。</p><p>目前模式：<span id="mode" class="badge">__MODE__</span> · <span id="status">狀態：__STATUS__</span> · 固定上游：<code id="upstream">__UPSTREAM__</code></p><p><button onclick="setWireMockMode('mock')">僅模擬</button><button onclick="setWireMockMode('proxy')">全部代理</button><button onclick="setWireMockMode('hybrid')">混合模式</button><button onclick="resetPreset()">還原啟動預設</button><button onclick="refresh()">重新整理映射與請求紀錄</button><button onclick="clearRequests()">清除請求紀錄</button></p><p>模式切換會更新原生 WireMock 映射，重新啟動後會回到啟動模式。上游只由啟動設定指定。混合模式以優先序 1 回應 MOCK-001 範例，其餘路徑以優先序 10 轉送。</p><p><a href="/control/mappings">原生映射 JSON</a> · <a href="/control/requests">原生請求紀錄 JSON</a> · <a href="http://localhost:8184">Microcks 操作介面</a> · <a href="http://localhost:8181">供應商沙盒</a></p><section><h2>實際原生映射</h2><pre id="mappings"></pre></section><section><h2>實際原生請求紀錄</h2><pre id="requests"></pre></section><script>
        async function setWireMockMode(mode) {
            let message = "模式套用失敗；請檢查目前狀態。";
            try {
                const response = await fetch("/control/mode", {
                    method: "POST",
                    headers: { "content-type": "application/json" },
                    body: JSON.stringify({ mode })
                });
                if (response.ok) {
                    return;
                }
                try {
                    const result = await response.json();
                    message = result.message || message;
                } catch {
                    message = `模式套用失敗（HTTP ${response.status}）；請檢查目前狀態。`;
                }
            } catch {
                message = "無法連線以套用模式；請檢查伺服器狀態。";
            } finally {
                await refresh();
            }
            alert(message);
        }

        async function resetPreset() {
            const response = await fetch("/control/reset", { method: "POST" });
            if (!response.ok) {
                alert("還原預設模式失敗；請檢查目前狀態。");
            }
            await refresh();
        }

        async function clearRequests() {
            await fetch("/control/requests", { method: "DELETE" });
            await refresh();
        }

        async function refresh() {
            const [stateResponse, mappingsResponse, requestsResponse] = await Promise.all([
                fetch("/control/state"),
                fetch("/control/mappings"),
                fetch("/control/requests")
            ]);
            const state = await stateResponse.json();
            document.getElementById("mode").textContent = state.mode || "無有效模式";
            document.getElementById("status").textContent = `狀態：${state.status}`;
            document.getElementById("upstream").textContent = state.upstream;
            document.getElementById("mappings").textContent = JSON.stringify(await mappingsResponse.json(), null, 2);
            document.getElementById("requests").textContent = JSON.stringify(await requestsResponse.json(), null, 2);
        }

        void refresh();
        setInterval(() => { void refresh(); }, 5000);
        </script></body></html>
        """;
}

/// <summary>供 ASP.NET Core 整合測試尋找產生的 Program 類別。</summary>
public partial class Program;
