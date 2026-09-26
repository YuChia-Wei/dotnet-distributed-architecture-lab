using Procurement.Domains;

namespace Procurement.Applications;

public interface IOperationUseCase<in TRequest, TResult>
{
    Task<TResult> ExecuteAsync(TRequest request, CancellationToken cancellationToken);
}

public sealed record CreatePurchase(PurchaseIdentity Identity);
public sealed record CreatePurchaseResult(PurchaseOrder Order, bool Created);
public sealed record ReconcilePurchase(Guid PurchaseOrderId);
public sealed record ReceiveGoods(Guid PurchaseOrderId, Guid ReceiptId, int Quantity);
public sealed record ReceiveGoodsResult(PurchaseOrder Order, GoodsReceipt Receipt, bool Created);

public sealed record SupplierQuote(string Sku, string Name, decimal UnitPrice, string Currency, string Origin);
public sealed record SupplierOrderOutcome(bool Accepted, string SupplierOrderId);

public enum SupplierLookupKind { Found, NotFound, Unknown }
public sealed record SupplierLookup(SupplierLookupKind Kind, SupplierOrderOutcome? Outcome = null);

public sealed class SupplierGatewayException(string code, string message) : Exception(message)
{
    public string Code { get; } = code;
}

public interface ISupplierGateway
{
    Task<SupplierQuote> QuoteAsync(string provider, string sku, CancellationToken cancellationToken);
    Task<SupplierOrderOutcome> SubmitAsync(PurchaseIdentity identity, CancellationToken cancellationToken);
    Task<SupplierLookup> LookupAsync(PurchaseIdentity identity, CancellationToken cancellationToken);
}

public interface IPurchaseOrderQueries
{
    Task<PurchaseOrder?> FindByIdAsync(Guid id, CancellationToken cancellationToken);
    Task<IReadOnlyList<PurchaseOrder>> RecentAsync(int limit, CancellationToken cancellationToken);
}

public interface IPurchaseCreationCommitter
{
    Task<CreatePurchaseResult> CreateOrGetAsync(PurchaseOrder candidate, CancellationToken cancellationToken);
}

public interface IPurchaseSubmissionCommitter
{
    Task<PurchaseOrder> ApplyOutcomeAsync(Guid id, SupplierOrderOutcome outcome, CancellationToken cancellationToken);
    Task<PurchaseOrder> MarkUnknownAsync(Guid id, CancellationToken cancellationToken);
}

public interface IGoodsReceiptCommitter
{
    Task<ReceiveGoodsResult> CommitAsync(Guid purchaseOrderId, Guid receiptId,
        Func<PurchaseOrder, ReceiveGoodsResult> decide, CancellationToken cancellationToken);
}

public sealed class CreatePurchaseUseCase(
    IPurchaseCreationCommitter creation, IPurchaseSubmissionCommitter submission,
    ISupplierGateway supplier) : IOperationUseCase<CreatePurchase, CreatePurchaseResult>
{
    public async Task<CreatePurchaseResult> ExecuteAsync(CreatePurchase request, CancellationToken cancellationToken)
    {
        var candidate = PurchaseOrder.Create(Guid.NewGuid(), request.Identity, DateTimeOffset.UtcNow);
        var persisted = await creation.CreateOrGetAsync(candidate, cancellationToken);
        persisted.Order.RequireIdentity(request.Identity);
        if (persisted.Order.State is not (PurchaseOrderState.PendingSubmission or PurchaseOrderState.SubmissionUnknown))
            return persisted;

        try
        {
            // The provider sees the original global key. There is deliberately no automatic POST retry.
            var result = await supplier.SubmitAsync(request.Identity, cancellationToken);
            var order = await submission.ApplyOutcomeAsync(persisted.Order.Id, result, CancellationToken.None);
            return new CreatePurchaseResult(order, persisted.Created);
        }
        catch (SupplierGatewayException ex) when (ex.Code is "supplier_identity_conflict" or "supplier_business_rejection")
        {
            throw;
        }
        catch (Exception ex) when (ex is SupplierGatewayException or HttpRequestException or TaskCanceledException or OperationCanceledException)
        {
            var order = await submission.MarkUnknownAsync(persisted.Order.Id, CancellationToken.None);
            return new CreatePurchaseResult(order, persisted.Created);
        }
    }
}

public sealed class ReconcilePurchaseUseCase(IPurchaseOrderQueries queries,
    IPurchaseSubmissionCommitter submission, ISupplierGateway supplier)
    : IOperationUseCase<ReconcilePurchase, PurchaseOrder>
{
    public async Task<PurchaseOrder> ExecuteAsync(ReconcilePurchase request, CancellationToken cancellationToken)
    {
        var order = await queries.FindByIdAsync(request.PurchaseOrderId, cancellationToken)
            ?? throw new ProcurementRuleException("purchase_not_found", "Purchase order was not found.");
        try
        {
            var found = await supplier.LookupAsync(order.Identity, cancellationToken);
            if (found.Kind == SupplierLookupKind.Found && found.Outcome is not null)
                return await submission.ApplyOutcomeAsync(order.Id, found.Outcome, cancellationToken);
            return order.State is PurchaseOrderState.PendingSubmission or PurchaseOrderState.SubmissionUnknown
                ? await submission.MarkUnknownAsync(order.Id, cancellationToken) : order;
        }
        catch (SupplierGatewayException ex) when (ex.Code == "supplier_identity_conflict")
        {
            throw;
        }
        catch (SupplierGatewayException ex) when (ex.Code == "supplier_invalid_response" &&
            order.State is not (PurchaseOrderState.PendingSubmission or PurchaseOrderState.SubmissionUnknown))
        {
            throw;
        }
        catch (Exception ex) when (ex is SupplierGatewayException or HttpRequestException or TaskCanceledException)
        {
            return order.State is PurchaseOrderState.PendingSubmission or PurchaseOrderState.SubmissionUnknown
                ? await submission.MarkUnknownAsync(order.Id, CancellationToken.None) : order;
        }
    }
}

public sealed class ReceiveGoodsUseCase(IGoodsReceiptCommitter committer)
    : IOperationUseCase<ReceiveGoods, ReceiveGoodsResult>
{
    public Task<ReceiveGoodsResult> ExecuteAsync(ReceiveGoods request, CancellationToken cancellationToken)
    {
        if (request.ReceiptId == Guid.Empty || request.Quantity <= 0)
            throw new ProcurementRuleException("invalid_receipt", "ReceiptId and positive quantity are required.");
        return committer.CommitAsync(request.PurchaseOrderId, request.ReceiptId, order =>
        {
            var prior = order.Receipts.FirstOrDefault(x => x.ReceiptId == request.ReceiptId);
            var receipt = order.Receive(request.ReceiptId, request.Quantity, DateTimeOffset.UtcNow);
            return new ReceiveGoodsResult(order, receipt, prior is null);
        }, cancellationToken);
    }
}
