using System.Collections.Concurrent;
using System.Text.RegularExpressions;
using Dapper;
using Npgsql;

var builder = WebApplication.CreateBuilder(args);
builder.WebHost.ConfigureKestrel(options => options.Limits.MaxRequestBodySize = 64 * 1024);
var connectionString = builder.Configuration.GetConnectionString("SupplierDb") ?? "Host=localhost;Port=5432;Database=supplier;Username=postgres;Password=postgres";
builder.Services.AddSingleton(NpgsqlDataSource.Create(connectionString));
builder.Services.AddSingleton<RequestJournal>();
builder.Services.AddSingleton<SupplierStore>();
builder.Services.AddSingleton<SandboxControl>();
var app = builder.Build();
var sqlPath = Path.Combine(AppContext.BaseDirectory,"sql","init.sql");
await using (var connection = await app.Services.GetRequiredService<NpgsqlDataSource>().OpenConnectionAsync())
    await connection.ExecuteAsync(await File.ReadAllTextAsync(sqlPath));

app.MapGet("/health", async (NpgsqlDataSource source, CancellationToken ct) => {
    try { await using var c = await source.OpenConnectionAsync(ct); await c.ExecuteScalarAsync<int>(new CommandDefinition("SELECT 1", cancellationToken: ct)); return Results.Ok(new {status="healthy"}); }
    catch { return Results.StatusCode(503); }
});
app.MapGet("/supplier/catalog/{sku}", async (string sku, SupplierStore store, RequestJournal log, HttpContext context, CancellationToken ct) => {
    log.Record("GET",$"/supplier/catalog/{sku}",null); var quote=await store.FindQuoteAsync(sku,ct);
    if (quote is null) return Results.NotFound(new ErrorResponse("unknown_sku","The supplier SKU was not found.")); context.Response.Headers["X-Supplier-Origin"]="sandbox"; return Results.Ok(quote);
});
app.MapPost("/supplier/orders", async (SupplierOrderRequest request, SupplierStore store, RequestJournal log, SandboxControl control, HttpContext context, CancellationToken ct) => {
    log.Record("POST","/supplier/orders",request.ClientRequestId);
    if(request.ClientRequestId==Guid.Empty || !SupplierStore.IsValidSku(request.Sku) || request.Quantity<=0 || request.UnitPrice<0 || request.Currency!="TWD") return Results.BadRequest(new ErrorResponse("invalid_order","clientRequestId, SKU, quantity, price, or currency is invalid."));
    var result=await store.CreateOrReplayAsync(request,ct);
    if(result.Conflict) return Results.Conflict(new ErrorResponse("idempotency_conflict","clientRequestId is already bound to a different typed payload."));
    if(result.Order is null) return Results.BadRequest(new ErrorResponse("quote_mismatch","SKU quote, price, or currency does not match."));
    context.Response.Headers["X-Supplier-Origin"]="sandbox";
    if(control.DelayAfterCommitMs>0) await Task.Delay(control.DelayAfterCommitMs,ct);
    return Results.Ok(result.Order);
});
app.MapGet("/supplier/orders/by-client-request/{id:guid}", async (Guid id,SupplierStore store,RequestJournal log,HttpContext context,CancellationToken ct) => {
    log.Record("GET",$"/supplier/orders/by-client-request/{id}",id); var order=await store.FindOrderAsync(id,ct);
    if (order is null) return Results.NotFound(new ErrorResponse("order_not_found","No supplier order has this clientRequestId.")); context.Response.Headers["X-Supplier-Origin"]="sandbox"; return Results.Ok(order);
});
app.MapGet("/sandbox/orders",async (SupplierStore s,CancellationToken ct)=>Results.Ok(await s.GetRecentOrdersAsync(ct)));
app.MapGet("/sandbox/requests",(RequestJournal j)=>Results.Ok(j.Recent));
app.MapGet("/sandbox/control",(SandboxControl c)=>Results.Ok(new SandboxControlResponse(c.DelayAfterCommitMs,"transient until process restart")));
app.MapPut("/sandbox/control",(SandboxControlRequest r,SandboxControl c)=>{ if(r.DelayAfterCommitMs is <0 or >10000) return Results.BadRequest(new ErrorResponse("invalid_delay","delayAfterCommitMs must be between 0 and 10000.")); c.DelayAfterCommitMs=r.DelayAfterCommitMs; return Results.Ok(new SandboxControlResponse(c.DelayAfterCommitMs,"transient until process restart")); });
app.MapGet("/",()=>Results.Content(SandboxPage.Html,"text/html; charset=utf-8"));
app.Run();

public sealed record SupplierQuote(string Sku,string Name,decimal UnitPrice,string Currency) { public string Origin => "sandbox"; }
public sealed record SupplierOrderRequest(Guid ClientRequestId,string Sku,int Quantity,decimal UnitPrice,string Currency);
public sealed record SupplierOrderResponse(string SupplierOrderId,Guid ClientRequestId,string Sku,int Quantity,decimal UnitPrice,string Currency,string Status,string Origin="sandbox");
public sealed record ErrorResponse(string Code,string Message);
public sealed record SandboxControlRequest(int DelayAfterCommitMs);
public sealed record SandboxControlResponse(int DelayAfterCommitMs,string Persistence);
public sealed record RequestObservation(DateTimeOffset Timestamp,string Method,string Path,Guid? ClientRequestId);
public sealed class SandboxControl { public int DelayAfterCommitMs {get;set;} }
public sealed class RequestJournal {
  private readonly ConcurrentQueue<RequestObservation> items=new();
  public IReadOnlyList<RequestObservation> Recent=>items.ToArray().Reverse().Take(100).ToArray();
  public void Record(string method,string path,Guid? id){items.Enqueue(new(DateTimeOffset.UtcNow,method,path,id));while(items.Count>100&&items.TryDequeue(out _)){} }
}
public sealed class SupplierStore(NpgsqlDataSource source) {
  private static readonly Regex Sku=new("^[A-Za-z0-9_-]{1,64}$",RegexOptions.CultureInvariant|RegexOptions.Compiled);
  public static bool IsValidSku(string? sku)=>sku is not null&&Sku.IsMatch(sku);
  public async Task<SupplierQuote?> FindQuoteAsync(string sku,CancellationToken ct){if(!IsValidSku(sku))return null; await using var c=await source.OpenConnectionAsync(ct); return await c.QuerySingleOrDefaultAsync<SupplierQuote>(new CommandDefinition("SELECT sku AS Sku,name AS Name,unit_price AS UnitPrice,currency AS Currency FROM supplier_skus WHERE sku=@Sku",new{Sku=sku},cancellationToken:ct));}
  public async Task<(SupplierOrderResponse? Order,bool Conflict)> CreateOrReplayAsync(SupplierOrderRequest r,CancellationToken ct){
    await using var c=await source.OpenConnectionAsync(ct); await using var tx=await c.BeginTransactionAsync(ct);
    var existing=await c.QuerySingleOrDefaultAsync<OrderRow>(new CommandDefinition("SELECT supplier_order_id AS SupplierOrderId,client_request_id AS ClientRequestId,sku AS Sku,quantity AS Quantity,unit_price AS UnitPrice,currency AS Currency,status AS Status FROM supplier_orders WHERE client_request_id=@Id FOR UPDATE",new{Id=r.ClientRequestId},tx,cancellationToken:ct));
    if(existing is not null){var same=SamePayload(existing,r);await tx.CommitAsync(ct);return same?(existing.ToResponse(),false):(null,true);}
    var quote=await c.QuerySingleOrDefaultAsync<SkuRow>(new CommandDefinition("SELECT sku AS Sku,unit_price AS UnitPrice,currency AS Currency,order_allowed AS OrderAllowed FROM supplier_skus WHERE sku=@Sku FOR SHARE",new{r.Sku},tx,cancellationToken:ct));
    if(quote is null||quote.UnitPrice!=r.UnitPrice||quote.Currency!=r.Currency){existing=await c.QuerySingleOrDefaultAsync<OrderRow>(new CommandDefinition("SELECT supplier_order_id AS SupplierOrderId,client_request_id AS ClientRequestId,sku AS Sku,quantity AS Quantity,unit_price AS UnitPrice,currency AS Currency,status AS Status FROM supplier_orders WHERE client_request_id=@Id FOR UPDATE",new{Id=r.ClientRequestId},tx,cancellationToken:ct));if(existing is not null){var same=SamePayload(existing,r);await tx.CommitAsync(ct);return same?(existing.ToResponse(),false):(null,true);}await tx.RollbackAsync(ct);return(null,false);}
    var id=Guid.NewGuid(); var status=quote.OrderAllowed?"accepted":"rejected";
    var inserted=await c.QuerySingleOrDefaultAsync<Guid?>(new CommandDefinition("INSERT INTO supplier_orders(supplier_order_id,client_request_id,sku,quantity,unit_price,currency,status) VALUES(@OrderId,@ClientRequestId,@Sku,@Quantity,@UnitPrice,@Currency,@Status) ON CONFLICT(client_request_id) DO NOTHING RETURNING supplier_order_id",new{OrderId=id,r.ClientRequestId,r.Sku,r.Quantity,r.UnitPrice,r.Currency,Status=status},tx,cancellationToken:ct));
    if(inserted is not null){await tx.CommitAsync(ct);return(new(id.ToString(),r.ClientRequestId,r.Sku,r.Quantity,r.UnitPrice,r.Currency,status),false);}
    existing=await c.QuerySingleAsync<OrderRow>(new CommandDefinition("SELECT supplier_order_id AS SupplierOrderId,client_request_id AS ClientRequestId,sku AS Sku,quantity AS Quantity,unit_price AS UnitPrice,currency AS Currency,status AS Status FROM supplier_orders WHERE client_request_id=@Id FOR UPDATE",new{Id=r.ClientRequestId},tx,cancellationToken:ct));
    await tx.CommitAsync(ct); return SamePayload(existing,r)?(existing.ToResponse(),false):(null,true);
  }
  private static bool SamePayload(OrderRow order,SupplierOrderRequest request)=>order.Sku==request.Sku&&order.Quantity==request.Quantity&&order.UnitPrice==request.UnitPrice&&order.Currency==request.Currency;  public async Task<SupplierOrderResponse?> FindOrderAsync(Guid id,CancellationToken ct){await using var c=await source.OpenConnectionAsync(ct);var row=await c.QuerySingleOrDefaultAsync<OrderRow>(new CommandDefinition("SELECT supplier_order_id AS SupplierOrderId,client_request_id AS ClientRequestId,sku AS Sku,quantity AS Quantity,unit_price AS UnitPrice,currency AS Currency,status AS Status FROM supplier_orders WHERE client_request_id=@Id",new{Id=id},cancellationToken:ct));return row?.ToResponse();}
  public async Task<IReadOnlyList<SupplierOrderResponse>> GetRecentOrdersAsync(CancellationToken ct){await using var c=await source.OpenConnectionAsync(ct);var rows=await c.QueryAsync<OrderRow>(new CommandDefinition("SELECT supplier_order_id AS SupplierOrderId,client_request_id AS ClientRequestId,sku AS Sku,quantity AS Quantity,unit_price AS UnitPrice,currency AS Currency,status AS Status FROM supplier_orders ORDER BY created_at DESC LIMIT 100",cancellationToken:ct));return rows.Select(x=>x.ToResponse()).ToArray();}
  private sealed record SkuRow(string Sku,decimal UnitPrice,string Currency,bool OrderAllowed);
  private sealed record OrderRow(Guid SupplierOrderId,Guid ClientRequestId,string Sku,int Quantity,decimal UnitPrice,string Currency,string Status){public SupplierOrderResponse ToResponse()=>new(SupplierOrderId.ToString(),ClientRequestId,Sku,Quantity,UnitPrice,Currency,Status);}
}
public static class SandboxPage { public const string Html="""
<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Supplier Sandbox</title><style>body{font:16px system-ui;max-width:1000px;margin:2rem auto;padding:0 1rem;color:#172033}button,input{padding:.5rem}section{border:1px solid #ccd4e0;border-radius:8px;padding:1rem;margin:1rem 0}pre{white-space:pre-wrap;background:#f2f5f9;padding:1rem;max-height:18rem;overflow:auto}</style></head><body><h1>SupplierSandbox.WebApi</h1><p>Local supplier provider with durable PostgreSQL order identity. Responses identify origin <code>sandbox</code>. The request journal retains only time, method, route and clientRequestId; it does not store arbitrary headers or bodies.</p><section><h2>Transient fault control</h2><label>Delay after committed order (ms) <input id="delay" type="number" min="0" max="10000" value="0"></label> <button onclick="saveDelay()">Apply</button><span id="state">Resets to zero on restart.</span></section><section><h2>Submit a sample order</h2><label>Client request ID <input id="clientId" value="9d4c99da-6517-46b2-baa7-7e81106d3d34"></label> <button onclick="refreshId()">New ID</button><br><label>SKU <input id="sku" value="REAL-001"></label> <label>Quantity <input id="quantity" type="number" min="1" value="2"></label><button onclick="submitOrder()">Submit to sandbox</button><pre id="submission"></pre></section><section><h2>Orders</h2><button onclick="refresh()">Refresh</button><pre id="orders"></pre></section><section><h2>Recent requests</h2><pre id="requests"></pre></section><section><h2>Example</h2><pre>GET /supplier/catalog/REAL-001
POST /supplier/orders
{"clientRequestId":"9d4c99da-6517-46b2-baa7-7e81106d3d34","sku":"REAL-001","quantity":2,"unitPrice":100,"currency":"TWD"}
GET /supplier/orders/by-client-request/9d4c99da-6517-46b2-baa7-7e81106d3d34</pre></section><script>function refreshId(){clientId.value=crypto.randomUUID()}async function submitOrder(){let payload={clientRequestId:clientId.value,sku:sku.value,quantity:Number(quantity.value),unitPrice:100,currency:"TWD"};let r=await fetch("/supplier/orders",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify(payload)});submission.textContent=r.status+" "+await r.text();refresh()}async function refresh(){for(const [p,i] of [['/sandbox/orders','orders'],['/sandbox/requests','requests']])document.getElementById(i).textContent=JSON.stringify(await(await fetch(p)).json(),null,2);let c=await(await fetch('/sandbox/control')).json();delay.value=c.delayAfterCommitMs;state.textContent=' '+c.persistence+'.'}async function saveDelay(){let r=await fetch('/sandbox/control',{method:'PUT',headers:{'content-type':'application/json'},body:JSON.stringify({delayAfterCommitMs:Number(delay.value)})});state.textContent=r.ok?'Applied; transient until restart.':'Rejected: use 0–10000 ms.';refresh()}refresh();setInterval(refresh,4000)</script></body></html>
"""; }
public partial class Program;
