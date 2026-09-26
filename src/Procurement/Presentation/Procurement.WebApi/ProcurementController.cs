using Microsoft.AspNetCore.Mvc;
using Procurement.Applications;
using Procurement.Domains;

namespace Procurement.WebApi;

/// <summary>採購單、供應商報價及實際收貨的入站 HTTP 轉接器。</summary>
[ApiController]
[Route("api/procurement")]
public sealed class ProcurementController(
    IOperationUseCase<QuoteSupplierInput, SupplierQuoteResponse> quote,
    IOperationUseCase<GetPurchaseInput, PurchaseOrderResponse> get,
    IOperationUseCase<ListPurchasesInput, IReadOnlyList<PurchaseOrderResponse>> list,
    IOperationUseCase<CreatePurchaseInput, CreatePurchaseOutput> create,
    IOperationUseCase<ReconcilePurchaseInput, PurchaseOrderResponse> reconcile,
    IOperationUseCase<ReceiveGoodsInput, ReceiveGoodsOutput> receive) : ControllerBase
{
    /// <summary>查詢指定供應商路徑及 SKU 的報價。</summary>
    [HttpGet("suppliers/{provider}/catalog/{sku}")]
    public async Task<ActionResult<SupplierQuoteResponse>> Quote(string provider, string sku,
        CancellationToken cancellationToken) =>
        Ok(await quote.ExecuteAsync(new QuoteSupplierInput(provider, sku), cancellationToken));

    /// <summary>以全域 clientRequestId 建立或安全重送單品採購。</summary>
    [HttpPost("purchase-orders")]
    public async Task<ActionResult<PurchaseOrderResponse>> Create(CreatePurchaseRequest request,
        CancellationToken cancellationToken)
    {
        var result = await create.ExecuteAsync(new CreatePurchaseInput(new PurchaseIdentity(request.ClientRequestId,
            request.ProductId, request.SupplierSku, request.Quantity, request.UnitPrice,
            request.Currency, request.Provider)), cancellationToken);
        if (result.Order.State is PurchaseOrderState.PendingSubmission or PurchaseOrderState.SubmissionUnknown)
            return AcceptedAtAction(nameof(Get), new { id = result.Order.Id }, result.Order);
        return result.Created
            ? CreatedAtAction(nameof(Get), new { id = result.Order.Id }, result.Order)
            : Ok(result.Order);
    }

    /// <summary>列出最近一百張採購單的唯讀快照。</summary>
    [HttpGet("purchase-orders")]
    public async Task<ActionResult<IReadOnlyList<PurchaseOrderResponse>>> List(CancellationToken cancellationToken) =>
        Ok(await list.ExecuteAsync(new ListPurchasesInput(), cancellationToken));

    /// <summary>依本地識別碼查詢採購單及其實際收貨。</summary>
    [HttpGet("purchase-orders/{id:guid}")]
    public async Task<ActionResult<PurchaseOrderResponse>> Get(Guid id, CancellationToken cancellationToken) =>
        Ok(await get.ExecuteAsync(new GetPurchaseInput(id), cancellationToken));

    /// <summary>以原始 clientRequestId 向原供應商路徑協調未知結果。</summary>
    [HttpPost("purchase-orders/{id:guid}/reconcile")]
    public async Task<ActionResult<PurchaseOrderResponse>> Reconcile(Guid id, CancellationToken cancellationToken)
    {
        var result = await reconcile.ExecuteAsync(new ReconcilePurchaseInput(id), cancellationToken);
        return result.State is PurchaseOrderState.PendingSubmission or PurchaseOrderState.SubmissionUnknown
            ? AcceptedAtAction(nameof(Get), new { id }, result)
            : Ok(result);
    }

    /// <summary>登錄實際收到的貨品；相同 ReceiptId 與內容可重播。</summary>
    [HttpPost("purchase-orders/{id:guid}/receipts")]
    public async Task<ActionResult<ReceiveGoodsOutput>> Receive(Guid id, ReceiveGoodsRequest request,
        CancellationToken cancellationToken)
    {
        var result = await receive.ExecuteAsync(new ReceiveGoodsInput(id, request.ReceiptId, request.Quantity), cancellationToken);
        return result.Created ? StatusCode(StatusCodes.Status201Created, result) : Ok(result);
    }
}

/// <summary>建立單品採購時不可變的輸入欄位。</summary>
public sealed record CreatePurchaseRequest(Guid ClientRequestId, Guid ProductId, string SupplierSku,
    int Quantity, decimal UnitPrice, string Currency, string Provider);
/// <summary>實際收貨的全域識別碼與正整數數量。</summary>
public sealed record ReceiveGoodsRequest(Guid ReceiptId, int Quantity);
