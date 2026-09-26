using Microsoft.AspNetCore.Mvc;
using Procurement.Applications;
using Procurement.Domains;

namespace Procurement.WebApi;

[ApiController]
[Route("api/procurement")]
public sealed class ProcurementController(
    ISupplierGateway supplier,
    IPurchaseOrderQueries queries,
    IOperationUseCase<CreatePurchase, CreatePurchaseResult> create,
    IOperationUseCase<ReconcilePurchase, PurchaseOrder> reconcile,
    IOperationUseCase<ReceiveGoods, ReceiveGoodsResult> receive) : ControllerBase
{
    [HttpGet("suppliers/{provider}/catalog/{sku}")]
    public async Task<ActionResult<SupplierQuote>> Quote(string provider, string sku, CancellationToken cancellationToken) =>
        Ok(await supplier.QuoteAsync(provider, sku, cancellationToken));

    [HttpPost("purchase-orders")]
    public async Task<ActionResult<PurchaseOrder>> Create(CreatePurchaseRequest request, CancellationToken cancellationToken)
    {
        var result = await create.ExecuteAsync(new CreatePurchase(new PurchaseIdentity(request.ClientRequestId,
            request.ProductId, request.SupplierSku, request.Quantity, request.UnitPrice,
            request.Currency, request.Provider)), cancellationToken);
        if (result.Order.State is PurchaseOrderState.PendingSubmission or PurchaseOrderState.SubmissionUnknown)
            return AcceptedAtAction(nameof(Get), new { id = result.Order.Id }, result.Order);
        return result.Created
            ? CreatedAtAction(nameof(Get), new { id = result.Order.Id }, result.Order)
            : Ok(result.Order);
    }

    [HttpGet("purchase-orders")]
    public async Task<ActionResult<IReadOnlyList<PurchaseOrder>>> List(CancellationToken cancellationToken) =>
        Ok(await queries.RecentAsync(100, cancellationToken));

    [HttpGet("purchase-orders/{id:guid}")]
    public async Task<ActionResult<PurchaseOrder>> Get(Guid id, CancellationToken cancellationToken) =>
        Ok(await queries.FindByIdAsync(id, cancellationToken)
            ?? throw new ProcurementRuleException("purchase_not_found", "Purchase order was not found."));

    [HttpPost("purchase-orders/{id:guid}/reconcile")]
    public async Task<ActionResult<PurchaseOrder>> Reconcile(Guid id, CancellationToken cancellationToken)
    {
        var result = await reconcile.ExecuteAsync(new ReconcilePurchase(id), cancellationToken);
        return result.State is PurchaseOrderState.PendingSubmission or PurchaseOrderState.SubmissionUnknown
            ? AcceptedAtAction(nameof(Get), new { id }, result)
            : Ok(result);
    }

    [HttpPost("purchase-orders/{id:guid}/receipts")]
    public async Task<ActionResult<ReceiveGoodsResult>> Receive(Guid id, ReceiveGoodsRequest request,
        CancellationToken cancellationToken)
    {
        var result = await receive.ExecuteAsync(new ReceiveGoods(id, request.ReceiptId, request.Quantity), cancellationToken);
        return result.Created ? StatusCode(StatusCodes.Status201Created, result) : Ok(result);
    }
}

public sealed record CreatePurchaseRequest(Guid ClientRequestId, Guid ProductId, string SupplierSku,
    int Quantity, decimal UnitPrice, string Currency, string Provider);
public sealed record ReceiveGoodsRequest(Guid ReceiptId, int Quantity);
