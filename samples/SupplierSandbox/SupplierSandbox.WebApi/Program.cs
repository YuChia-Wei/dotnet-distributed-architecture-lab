using System.Collections.Concurrent;
using System.Text.RegularExpressions;
using Dapper;
using Npgsql;

var builder = WebApplication.CreateBuilder(args);
builder.WebHost.ConfigureKestrel(options => options.Limits.MaxRequestBodySize = 64 * 1024);
var connectionString = builder.Configuration.GetConnectionString("SupplierDb")
    ?? "Host=localhost;Port=5432;Database=supplier;Username=postgres;Password=postgres";
builder.Services.AddSingleton(NpgsqlDataSource.Create(connectionString));
builder.Services.AddSingleton<RequestJournal>();
builder.Services.AddSingleton<SupplierStore>();
builder.Services.AddSingleton<SandboxControl>();

var app = builder.Build();
var sqlPath = Path.Combine(AppContext.BaseDirectory, "sql", "init.sql");
await using (var connection = await app.Services.GetRequiredService<NpgsqlDataSource>().OpenConnectionAsync())
{
    await connection.ExecuteAsync(await File.ReadAllTextAsync(sqlPath));
}

app.Use(async (context, next) =>
{
    if (!context.Request.Path.StartsWithSegments("/supplier"))
    {
        await next();
        return;
    }

    var originalBody = context.Response.Body;
    await using var responseBuffer = new MemoryStream();
    context.Response.Body = responseBuffer;
    try
    {
        await next();
        if (!context.Response.HasStarted)
        {
            context.Response.Headers.Remove("Transfer-Encoding");
            context.Response.ContentLength = responseBuffer.Length;
        }

        responseBuffer.Position = 0;
        await responseBuffer.CopyToAsync(originalBody, context.RequestAborted);
    }
    finally
    {
        context.Response.Body = originalBody;
    }
});

app.MapGet("/health", async (NpgsqlDataSource source, CancellationToken cancellationToken) =>
{
    try
    {
        await using var connection = await source.OpenConnectionAsync(cancellationToken);
        await connection.ExecuteScalarAsync<int>(
            new CommandDefinition("SELECT 1", cancellationToken: cancellationToken));
        return Results.Ok(new { status = "healthy" });
    }
    catch
    {
        return Results.StatusCode(503);
    }
});

app.MapGet("/supplier/catalog/{sku}", async (
    string sku,
    SupplierStore store,
    RequestJournal journal,
    HttpContext context,
    CancellationToken cancellationToken) =>
{
    journal.Record("GET", $"/supplier/catalog/{sku}", null);
    var quote = await store.FindQuoteAsync(sku, cancellationToken);
    if (quote is null)
    {
        return Results.NotFound(new ErrorResponse("unknown_sku", "找不到此供應商 SKU。"));
    }

    context.Response.Headers["X-Supplier-Origin"] = "sandbox";
    return Results.Ok(quote);
});

app.MapPost("/supplier/orders", async (
    SupplierOrderRequest request,
    SupplierStore store,
    RequestJournal journal,
    SandboxControl control,
    HttpContext context,
    CancellationToken cancellationToken) =>
{
    journal.Record("POST", "/supplier/orders", request.ClientRequestId);
    if (request.ClientRequestId == Guid.Empty
        || !SupplierStore.IsValidSku(request.Sku)
        || request.Quantity <= 0
        || request.UnitPrice < 0
        || request.Currency != "TWD")
    {
        return Results.BadRequest(new ErrorResponse(
            "invalid_order",
            "clientRequestId、SKU、數量、價格或幣別無效。"));
    }

    var result = await store.CreateOrReplayAsync(request, cancellationToken);
    if (result.Conflict)
    {
        return Results.Conflict(new ErrorResponse(
            "idempotency_conflict",
            "此 clientRequestId 已對應至不同的訂單內容。"));
    }

    if (result.Order is null)
    {
        return Results.BadRequest(new ErrorResponse("quote_mismatch", "SKU 報價、價格或幣別不相符。"));
    }

    context.Response.Headers["X-Supplier-Origin"] = "sandbox";
    if (control.DelayAfterCommitMs > 0)
    {
        await Task.Delay(control.DelayAfterCommitMs, cancellationToken);
    }

    return Results.Ok(result.Order);
});

app.MapGet("/supplier/orders/by-client-request/{id:guid}", async (
    Guid id,
    SupplierStore store,
    RequestJournal journal,
    HttpContext context,
    CancellationToken cancellationToken) =>
{
    journal.Record("GET", $"/supplier/orders/by-client-request/{id}", id);
    var order = await store.FindOrderAsync(id, cancellationToken);
    if (order is null)
    {
        return Results.NotFound(new ErrorResponse(
            "order_not_found",
            "找不到此 clientRequestId 的供應商訂單。"));
    }

    context.Response.Headers["X-Supplier-Origin"] = "sandbox";
    return Results.Ok(order);
});

app.MapGet("/sandbox/orders", async (SupplierStore store, CancellationToken cancellationToken) =>
    Results.Ok(await store.GetRecentOrdersAsync(cancellationToken)));
app.MapGet("/sandbox/requests", (RequestJournal journal) => Results.Ok(journal.Recent));
app.MapGet("/sandbox/control", (SandboxControl control) => Results.Ok(
    new SandboxControlResponse(control.DelayAfterCommitMs, "服務重新啟動後恢復為零")));
app.MapPut("/sandbox/control", (SandboxControlRequest request, SandboxControl control) =>
{
    if (request.DelayAfterCommitMs is < 0 or > 10000)
    {
        return Results.BadRequest(new ErrorResponse(
            "invalid_delay",
            "延遲時間必須介於 0 到 10000 毫秒。"));
    }

    control.DelayAfterCommitMs = request.DelayAfterCommitMs;
    return Results.Ok(new SandboxControlResponse(control.DelayAfterCommitMs, "服務重新啟動後恢復為零"));
});
app.MapGet("/", () => Results.Content(SandboxPage.Html, "text/html; charset=utf-8"));
app.Run();

/// <summary>代表供應商商品報價。</summary>
/// <param name="Sku">供應商商品識別碼。</param>
/// <param name="Name">商品名稱。</param>
/// <param name="UnitPrice">單件報價。</param>
/// <param name="Currency">報價幣別。</param>
public sealed record SupplierQuote(string Sku, string Name, decimal UnitPrice, string Currency)
{
    /// <summary>取得此報價的來源標記。</summary>
    public string Origin => "sandbox";
}

/// <summary>提交供應商訂單所需的欄位。</summary>
/// <param name="ClientRequestId">呼叫端提供的冪等識別碼。</param>
/// <param name="Sku">要訂購的供應商 SKU。</param>
/// <param name="Quantity">訂購數量。</param>
/// <param name="UnitPrice">呼叫端取得的單件報價。</param>
/// <param name="Currency">訂單幣別。</param>
public sealed record SupplierOrderRequest(
    Guid ClientRequestId,
    string Sku,
    int Quantity,
    decimal UnitPrice,
    string Currency);

/// <summary>供應商建立或重播訂單時回傳的內容。</summary>
/// <param name="SupplierOrderId">穩定的供應商訂單識別碼。</param>
/// <param name="ClientRequestId">呼叫端提供的冪等識別碼。</param>
/// <param name="Sku">已接受的供應商 SKU。</param>
/// <param name="Quantity">已接受的訂購數量。</param>
/// <param name="UnitPrice">已接受的單件價格。</param>
/// <param name="Currency">訂單幣別。</param>
/// <param name="Status">供應商接受或拒絕的狀態。</param>
/// <param name="Origin">供應商回應來源。</param>
public sealed record SupplierOrderResponse(
    string SupplierOrderId,
    Guid ClientRequestId,
    string Sku,
    int Quantity,
    decimal UnitPrice,
    string Currency,
    string Status,
    string Origin = "sandbox");

/// <summary>供應商沙盒 API 的錯誤內容。</summary>
/// <param name="Code">穩定的錯誤代碼。</param>
/// <param name="Message">供操作人員閱讀的錯誤說明。</param>
public sealed record ErrorResponse(string Code, string Message);

/// <summary>更新沙盒提交後延遲所需的設定。</summary>
/// <param name="DelayAfterCommitMs">資料提交後等待的毫秒數，範圍為 0 到 10000。</param>
public sealed record SandboxControlRequest(int DelayAfterCommitMs);

/// <summary>目前沙盒延遲設定與其保存方式。</summary>
/// <param name="DelayAfterCommitMs">資料提交後等待的毫秒數。</param>
/// <param name="Persistence">設定會保留多久的說明。</param>
public sealed record SandboxControlResponse(int DelayAfterCommitMs, string Persistence);

/// <summary>近期供應商 API 請求的安全摘要。</summary>
/// <param name="Timestamp">收到請求的 UTC 時間。</param>
/// <param name="Method">HTTP 方法。</param>
/// <param name="Path">請求路徑，不含任意標頭或本文。</param>
/// <param name="ClientRequestId">請求包含的用戶端識別碼；未提供時為 null。</param>
public sealed record RequestObservation(
    DateTimeOffset Timestamp,
    string Method,
    string Path,
    Guid? ClientRequestId);

/// <summary>保存只在目前服務程序有效的供應商延遲設定。</summary>
public sealed class SandboxControl
{
    /// <summary>取得或設定資料提交後的延遲毫秒數。</summary>
    public int DelayAfterCommitMs { get; set; }
}

/// <summary>保存數量有限且不含請求本文的近期請求摘要。</summary>
public sealed class RequestJournal
{
    private readonly ConcurrentQueue<RequestObservation> items = new();

    /// <summary>依時間倒序取得最近至多一百筆請求。</summary>
    public IReadOnlyList<RequestObservation> Recent => items.ToArray().Reverse().Take(100).ToArray();

    /// <summary>新增請求摘要，並移除超出保留上限的舊項目。</summary>
    /// <param name="method">HTTP 方法。</param>
    /// <param name="path">請求路徑。</param>
    /// <param name="id">可用的用戶端請求識別碼。</param>
    public void Record(string method, string path, Guid? id)
    {
        var boundedPath = path.Length <= 256 ? path : path[..256];
        items.Enqueue(new RequestObservation(DateTimeOffset.UtcNow, method, boundedPath, id));
        while (items.Count > 100 && items.TryDequeue(out _))
        {
        }
    }
}

/// <summary>以 PostgreSQL 讀取報價並持久化具冪等性的供應商訂單。</summary>
/// <param name="source">供應商資料庫連線來源。</param>
public sealed class SupplierStore(NpgsqlDataSource source)
{
    private static readonly Regex Sku = new(
        "^[A-Za-z0-9_-]{1,64}$",
        RegexOptions.CultureInvariant | RegexOptions.Compiled);

    /// <summary>檢查 SKU 是否符合供應商允許的有限格式。</summary>
    /// <param name="sku">待檢查的 SKU。</param>
    /// <returns>SKU 是否有效。</returns>
    public static bool IsValidSku(string? sku) => sku is not null && Sku.IsMatch(sku);

    /// <summary>依 SKU 讀取目前報價。</summary>
    /// <param name="sku">要查詢的 SKU。</param>
    /// <param name="ct">取消操作的權杖。</param>
    /// <returns>存在時的報價，否則為 null。</returns>
    public async Task<SupplierQuote?> FindQuoteAsync(string sku, CancellationToken ct)
    {
        if (!IsValidSku(sku))
        {
            return null;
        }

        await using var connection = await source.OpenConnectionAsync(ct);
        return await connection.QuerySingleOrDefaultAsync<SupplierQuote>(new CommandDefinition(
            "SELECT sku AS Sku,name AS Name,unit_price AS UnitPrice,currency AS Currency FROM supplier_skus WHERE sku=@Sku",
            new { Sku = sku },
            cancellationToken: ct));
    }

    /// <summary>依 clientRequestId 建立訂單或回傳相同內容的既有訂單。</summary>
    /// <param name="request">提交的訂單欄位。</param>
    /// <param name="ct">取消操作的權杖。</param>
    /// <returns>訂單與衝突旗標；不符報價時訂單為 null。</returns>
    public async Task<(SupplierOrderResponse? Order, bool Conflict)> CreateOrReplayAsync(
        SupplierOrderRequest request,
        CancellationToken ct)
    {
        await using var connection = await source.OpenConnectionAsync(ct);
        await using var transaction = await connection.BeginTransactionAsync(ct);
        var existing = await FindOrderRowAsync(connection, transaction, request.ClientRequestId, ct);
        if (existing is not null)
        {
            var samePayload = SamePayload(existing, request);
            await transaction.CommitAsync(ct);
            return samePayload ? (existing.ToResponse(), false) : (null, true);
        }

        var quote = await connection.QuerySingleOrDefaultAsync<SkuRow>(new CommandDefinition(
            "SELECT sku AS Sku,unit_price AS UnitPrice,currency AS Currency,order_allowed AS OrderAllowed FROM supplier_skus WHERE sku=@Sku FOR SHARE",
            new { request.Sku },
            transaction,
            cancellationToken: ct));
        if (quote is null || quote.UnitPrice != request.UnitPrice || quote.Currency != request.Currency)
        {
            existing = await FindOrderRowAsync(connection, transaction, request.ClientRequestId, ct);
            if (existing is not null)
            {
                var samePayload = SamePayload(existing, request);
                await transaction.CommitAsync(ct);
                return samePayload ? (existing.ToResponse(), false) : (null, true);
            }

            await transaction.RollbackAsync(ct);
            return (null, false);
        }

        var orderId = Guid.NewGuid();
        var status = quote.OrderAllowed ? "accepted" : "rejected";
        var inserted = await connection.QuerySingleOrDefaultAsync<Guid?>(new CommandDefinition(
            "INSERT INTO supplier_orders(supplier_order_id,client_request_id,sku,quantity,unit_price,currency,status) VALUES(@OrderId,@ClientRequestId,@Sku,@Quantity,@UnitPrice,@Currency,@Status) ON CONFLICT(client_request_id) DO NOTHING RETURNING supplier_order_id",
            new
            {
                OrderId = orderId,
                request.ClientRequestId,
                request.Sku,
                request.Quantity,
                request.UnitPrice,
                request.Currency,
                Status = status
            },
            transaction,
            cancellationToken: ct));
        if (inserted is not null)
        {
            await transaction.CommitAsync(ct);
            return (new SupplierOrderResponse(
                orderId.ToString(),
                request.ClientRequestId,
                request.Sku,
                request.Quantity,
                request.UnitPrice,
                request.Currency,
                status), false);
        }

        existing = await FindOrderRowAsync(connection, transaction, request.ClientRequestId, ct)
            ?? throw new InvalidOperationException("Concurrent supplier order insert did not produce a row.");
        await transaction.CommitAsync(ct);
        return SamePayload(existing, request)
            ? (existing.ToResponse(), false)
            : (null, true);
    }

    /// <summary>依呼叫端識別碼讀取已儲存的供應商訂單。</summary>
    /// <param name="id">呼叫端訂單識別碼。</param>
    /// <param name="ct">取消操作的權杖。</param>
    /// <returns>已儲存的訂單，找不到時為 null。</returns>
    public async Task<SupplierOrderResponse?> FindOrderAsync(Guid id, CancellationToken ct)
    {
        await using var connection = await source.OpenConnectionAsync(ct);
        var row = await connection.QuerySingleOrDefaultAsync<OrderRow>(new CommandDefinition(
            "SELECT supplier_order_id AS SupplierOrderId,client_request_id AS ClientRequestId,sku AS Sku,quantity AS Quantity,unit_price AS UnitPrice,currency AS Currency,status AS Status FROM supplier_orders WHERE client_request_id=@Id",
            new { Id = id },
            cancellationToken: ct));
        return row?.ToResponse();
    }

    /// <summary>依建立時間倒序讀取最近至多一百筆訂單。</summary>
    /// <param name="ct">取消操作的權杖。</param>
    /// <returns>近期供應商訂單。</returns>
    public async Task<IReadOnlyList<SupplierOrderResponse>> GetRecentOrdersAsync(CancellationToken ct)
    {
        await using var connection = await source.OpenConnectionAsync(ct);
        var rows = await connection.QueryAsync<OrderRow>(new CommandDefinition(
            "SELECT supplier_order_id AS SupplierOrderId,client_request_id AS ClientRequestId,sku AS Sku,quantity AS Quantity,unit_price AS UnitPrice,currency AS Currency,status AS Status FROM supplier_orders ORDER BY created_at DESC LIMIT 100",
            cancellationToken: ct));
        return rows.Select(row => row.ToResponse()).ToArray();
    }

    private static async Task<OrderRow?> FindOrderRowAsync(
        NpgsqlConnection connection,
        NpgsqlTransaction transaction,
        Guid id,
        CancellationToken ct) =>
        await connection.QuerySingleOrDefaultAsync<OrderRow>(new CommandDefinition(
            "SELECT supplier_order_id AS SupplierOrderId,client_request_id AS ClientRequestId,sku AS Sku,quantity AS Quantity,unit_price AS UnitPrice,currency AS Currency,status AS Status FROM supplier_orders WHERE client_request_id=@Id FOR UPDATE",
            new { Id = id },
            transaction,
            cancellationToken: ct));

    private static bool SamePayload(OrderRow order, SupplierOrderRequest request) =>
        order.Sku == request.Sku
        && order.Quantity == request.Quantity
        && order.UnitPrice == request.UnitPrice
        && order.Currency == request.Currency;

    private sealed record SkuRow(string Sku, decimal UnitPrice, string Currency, bool OrderAllowed);

    private sealed record OrderRow(
        Guid SupplierOrderId,
        Guid ClientRequestId,
        string Sku,
        int Quantity,
        decimal UnitPrice,
        string Currency,
        string Status)
    {
        public SupplierOrderResponse ToResponse() => new(
            SupplierOrderId.ToString(),
            ClientRequestId,
            Sku,
            Quantity,
            UnitPrice,
            Currency,
            Status);
    }
}

/// <summary>提供操作人員建立測試訂單與檢視沙盒狀態的繁體中文頁面。</summary>
public static class SandboxPage
{
    /// <summary>供應商沙盒操作頁面的 HTML。</summary>
    public const string Html = """
        <!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>供應商沙盒</title><style>body{font:16px system-ui;max-width:1000px;margin:2rem auto;padding:0 1rem;color:#172033}button,input{padding:.5rem}section{border:1px solid #ccd4e0;border-radius:8px;padding:1rem;margin:1rem 0}pre{white-space:pre-wrap;background:#f2f5f9;padding:1rem;max-height:18rem;overflow:auto}</style></head><body><h1>SupplierSandbox.WebApi 供應商沙盒</h1><p>本機供應商服務使用 PostgreSQL 保存訂單識別碼。成功回應會標示來源 <code>sandbox</code>。近期請求紀錄只保存時間、方法、路徑與 clientRequestId，不保存任意標頭或本文。</p><section><h2>暫時性故障控制</h2><label>訂單提交後延遲（毫秒） <input id="delay" type="number" min="0" max="10000" value="0"></label> <button onclick="saveDelay()">套用</button><span id="state">重新啟動後恢復為零。</span></section><section><h2>提交範例訂單</h2><label>用戶端請求識別碼 <input id="clientId" value="9d4c99da-6517-46b2-baa7-7e81106d3d34"></label> <button onclick="refreshId()">產生新識別碼</button><br><label>SKU <input id="sku" value="REAL-001"></label> <label>數量 <input id="quantity" type="number" min="1" value="2"></label><button onclick="submitOrder()">提交至沙盒</button><pre id="submission"></pre></section><section><h2>近期訂單</h2><button onclick="refresh()">重新整理</button><pre id="orders"></pre></section><section><h2>近期請求</h2><pre id="requests"></pre></section><section><h2>範例請求</h2><pre>GET /supplier/catalog/REAL-001
        POST /supplier/orders
        {"clientRequestId":"9d4c99da-6517-46b2-baa7-7e81106d3d34","sku":"REAL-001","quantity":2,"unitPrice":100,"currency":"TWD"}
        GET /supplier/orders/by-client-request/9d4c99da-6517-46b2-baa7-7e81106d3d34</pre></section><script>function refreshId(){clientId.value=crypto.randomUUID()}async function submitOrder(){let payload={clientRequestId:clientId.value,sku:sku.value,quantity:Number(quantity.value),unitPrice:100,currency:"TWD"};let r=await fetch("/supplier/orders",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify(payload)});submission.textContent=r.status+" "+await r.text();refresh()}async function refresh(){for(const [p,i] of [['/sandbox/orders','orders'],['/sandbox/requests','requests']])document.getElementById(i).textContent=JSON.stringify(await(await fetch(p)).json(),null,2);let c=await(await fetch('/sandbox/control')).json();if(document.activeElement!==delay)delay.value=c.delayAfterCommitMs;if(state.dataset.feedback!=='error')state.textContent=' '+c.persistence+'.'}async function saveDelay(){let r=await fetch('/sandbox/control',{method:'PUT',headers:{'content-type':'application/json'},body:JSON.stringify({delayAfterCommitMs:Number(delay.value)})});if(!r.ok){state.dataset.feedback='error';state.textContent='拒絕設定，請填入 0 到 10000 毫秒。';return}state.dataset.feedback='';state.textContent='已套用；服務重新啟動後恢復。';refresh()}refresh();setInterval(refresh,4000)}</script></body></html>
        """;
}

/// <summary>供 ASP.NET Core 整合測試尋找產生的 Program 類別。</summary>
public partial class Program;
