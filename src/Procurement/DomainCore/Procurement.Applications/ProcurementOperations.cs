using Lab.BuildingBlocks.Application;
using Procurement.Domains;

namespace Procurement.Applications;

/// <summary>單一入站操作的應用程式邊界。</summary>
public interface IOperationUseCase<in TInput, TOutput>
{
    /// <summary>執行操作並回傳不可變輸出。</summary>
    Task<TOutput> ExecuteAsync(TInput input, CancellationToken cancellationToken);
}

/// <summary>建立或重送單品採購單。</summary>
public sealed record CreatePurchaseInput(PurchaseIdentity Identity);
/// <summary>採購建立結果；Created 僅表示本地身分首次建立。</summary>
public sealed record CreatePurchaseOutput(PurchaseOrderResponse Order, bool Created);
/// <summary>依原供應商路徑查單並協調未知結果。</summary>
public sealed record ReconcilePurchaseInput(Guid PurchaseOrderId);
/// <summary>登錄實際收貨，不代表供應商接單。</summary>
public sealed record ReceiveGoodsInput(Guid PurchaseOrderId, Guid ReceiptId, int Quantity);
/// <summary>收貨後的本地狀態與原始收貨事實。</summary>
public sealed record ReceiveGoodsOutput(PurchaseOrderResponse Order, GoodsReceiptResponse Receipt, bool Created);
/// <summary>查詢單張採購單。</summary>
public sealed record GetPurchaseInput(Guid PurchaseOrderId);
/// <summary>查詢最近的採購單，最多一百張。</summary>
public sealed record ListPurchasesInput(int Limit = 100);
/// <summary>查詢指定供應商路徑的商品報價。</summary>
public sealed record QuoteSupplierInput(string Provider, string Sku);

/// <summary>公開的不可變收貨查詢投影。</summary>
public sealed record GoodsReceiptResponse(Guid ReceiptId, Guid PurchaseOrderId, Guid ProductId,
    int Quantity, DateTimeOffset ReceivedAt)
{
    /// <summary>從聚合擁有的收貨事實建立公開投影。</summary>
    public static GoodsReceiptResponse From(GoodsReceipt receipt) =>
        new(receipt.ReceiptId, receipt.PurchaseOrderId, receipt.ProductId, receipt.Quantity, receipt.ReceivedAt);
}

/// <summary>公開的不可變送單身分投影。</summary>
public sealed record PurchaseIdentityResponse(Guid ClientRequestId, Guid ProductId, string SupplierSku,
    int Quantity, decimal UnitPrice, string Currency, string Provider);

/// <summary>公開的不可變採購查詢投影，不洩漏可變聚合。</summary>
public sealed record PurchaseOrderResponse(Guid Id, PurchaseIdentityResponse Identity,
    PurchaseOrderState State, string? SupplierOrderId, int ReceivedQuantity, int Version,
    DateTimeOffset CreatedAt, DateTimeOffset UpdatedAt, IReadOnlyList<GoodsReceiptResponse> Receipts)
{
    /// <summary>從目前聚合狀態建立獨立的查詢快照。</summary>
    public static PurchaseOrderResponse From(PurchaseOrder order) =>
        new(order.Id, new PurchaseIdentityResponse(order.Identity.ClientRequestId, order.Identity.ProductId,
            order.Identity.SupplierSku, order.Identity.Quantity, order.Identity.UnitPrice,
            order.Identity.Currency, order.Identity.Provider), order.State, order.SupplierOrderId,
            order.ReceivedQuantity, order.Version, order.CreatedAt, order.UpdatedAt,
            Array.AsReadOnly(order.Receipts.Select(GoodsReceiptResponse.From).ToArray()));
}

/// <summary>供應商報價的應用層資料，不暴露供應商專屬 DTO。</summary>
public sealed record SupplierQuoteResponse(string Sku, string Name, decimal UnitPrice, string Currency, string Origin);
/// <summary>已驗證身分後的供應商接單結果。</summary>
public sealed record SupplierOrderOutcome(bool Accepted, string SupplierOrderId);
/// <summary>查單結果類別；查無訂單與交通失敗分開處理。</summary>
public enum SupplierLookupKind { Found, NotFound, Unknown }
/// <summary>供應商依原始 clientRequestId 查單的結果。</summary>
public sealed record SupplierLookup(SupplierLookupKind Kind, SupplierOrderOutcome? Outcome = null);

/// <summary>供應商通訊或回應的可攜式錯誤。</summary>
public sealed class SupplierGatewayException(string code, string message) : Exception(message)
{
    /// <summary>穩定的錯誤代碼。</summary>
    public string Code { get; } = code;
}

/// <summary>應用層持有的供應商查價、送單與查單埠。</summary>
public interface ISupplierGateway
{
    /// <summary>取得指定 SKU 的報價。</summary>
    Task<SupplierQuoteResponse> QuoteAsync(string provider, string sku, CancellationToken cancellationToken);
    /// <summary>以原始全域冪等鍵送出訂單。</summary>
    Task<SupplierOrderOutcome> SubmitAsync(PurchaseIdentity identity, CancellationToken cancellationToken);
    /// <summary>以原始全域冪等鍵查詢供應商訂單。</summary>
    Task<SupplierLookup> LookupAsync(PurchaseIdentity identity, CancellationToken cancellationToken);
}

/// <summary>應用操作使用的聚合載入埠。</summary>
public interface IPurchaseOrderRepository
{
    /// <summary>依本地識別碼載入聚合供業務決策使用。</summary>
    Task<PurchaseOrder?> FindByIdAsync(Guid id, CancellationToken cancellationToken);
}

/// <summary>唯讀查詢埠，只回傳公開投影。</summary>
public interface IPurchaseOrderQueries : IQueryRepository
{
    /// <summary>依本地識別碼查詢採購快照。</summary>
    Task<PurchaseOrderResponse?> GetByIdAsync(Guid id, CancellationToken cancellationToken);
    /// <summary>依建立時間查詢最多一百筆快照。</summary>
    Task<IReadOnlyList<PurchaseOrderResponse>> RecentAsync(int limit, CancellationToken cancellationToken);
}

/// <summary>本地採購身分的原子建立結果。</summary>
public sealed record CreateCommittedPurchase(PurchaseOrder Order, bool Created);
/// <summary>建立或取得唯一 clientRequestId 的採購身分。</summary>
public interface IPurchaseCreationCommitter
{
    /// <summary>只在首次建立時插入；相同鍵回傳既存聚合。</summary>
    Task<CreateCommittedPurchase> CreateOrGetAsync(PurchaseOrder candidate, CancellationToken cancellationToken);
}

/// <summary>供應商狀態的本地條件式提交埠。</summary>
public interface IPurchaseSubmissionCommitter
{
    /// <summary>提交已驗證的供應商結果，不覆寫已確定的相反結果。</summary>
    Task<PurchaseOrder> ApplyOutcomeAsync(Guid id, SupplierOrderOutcome outcome, CancellationToken cancellationToken);
    /// <summary>只將未確定的訂單標示為結果未知。</summary>
    Task<PurchaseOrder> MarkUnknownAsync(Guid id, CancellationToken cancellationToken);
}

/// <summary>收貨交易內的聚合決策與來源 outbox 提交結果。</summary>
public sealed record ReceiptCommitResult(PurchaseOrder Order, GoodsReceipt Receipt, bool Created);
/// <summary>收貨與訊息來源紀錄的單一交易提交埠。</summary>
public interface IGoodsReceiptCommitter
{
    /// <summary>鎖定聚合後執行純本地決策，並原子提交新收貨與 outbox。</summary>
    Task<ReceiptCommitResult> CommitAsync(Guid purchaseOrderId, Guid receiptId,
        Func<PurchaseOrder, ReceiptCommitResult> decide, CancellationToken cancellationToken);
}

/// <summary>查詢供應商報價的入站用例。</summary>
public sealed class QuoteSupplierUseCase(ISupplierGateway supplier)
    : IOperationUseCase<QuoteSupplierInput, SupplierQuoteResponse>
{
    /// <inheritdoc />
    public Task<SupplierQuoteResponse> ExecuteAsync(QuoteSupplierInput input, CancellationToken cancellationToken) =>
        supplier.QuoteAsync(input.Provider, input.Sku, cancellationToken);
}

/// <summary>查詢單張採購快照的入站用例。</summary>
public sealed class GetPurchaseUseCase(IPurchaseOrderQueries queries)
    : IOperationUseCase<GetPurchaseInput, PurchaseOrderResponse>
{
    /// <inheritdoc />
    public async Task<PurchaseOrderResponse> ExecuteAsync(GetPurchaseInput input, CancellationToken cancellationToken) =>
        await queries.GetByIdAsync(input.PurchaseOrderId, cancellationToken)
        ?? throw new ProcurementRuleException("purchase_not_found", "Purchase order was not found.");
}

/// <summary>查詢最近採購快照的入站用例。</summary>
public sealed class ListPurchasesUseCase(IPurchaseOrderQueries queries)
    : IOperationUseCase<ListPurchasesInput, IReadOnlyList<PurchaseOrderResponse>>
{
    /// <inheritdoc />
    public Task<IReadOnlyList<PurchaseOrderResponse>> ExecuteAsync(ListPurchasesInput input, CancellationToken cancellationToken) =>
        queries.RecentAsync(Math.Clamp(input.Limit, 1, 100), cancellationToken);
}

/// <summary>保留本地冪等身分後送單的入站用例。</summary>
public sealed class CreatePurchaseUseCase(IPurchaseCreationCommitter creation,
    IPurchaseSubmissionCommitter submission, ISupplierGateway supplier)
    : IOperationUseCase<CreatePurchaseInput, CreatePurchaseOutput>
{
    /// <inheritdoc />
    public async Task<CreatePurchaseOutput> ExecuteAsync(CreatePurchaseInput input, CancellationToken cancellationToken)
    {
        var candidate = PurchaseOrder.Create(Guid.NewGuid(), input.Identity, DateTimeOffset.UtcNow);
        var persisted = await creation.CreateOrGetAsync(candidate, cancellationToken);
        persisted.Order.RequireIdentity(input.Identity);
        if (persisted.Order.State is not (PurchaseOrderState.PendingSubmission or PurchaseOrderState.SubmissionUnknown))
            return new CreatePurchaseOutput(PurchaseOrderResponse.From(persisted.Order), persisted.Created);

        try
        {
            // 供應商只收到原始 key；不在 HTTP 層自動重送 POST。
            var result = await supplier.SubmitAsync(input.Identity, cancellationToken);
            var order = await submission.ApplyOutcomeAsync(persisted.Order.Id, result, CancellationToken.None);
            return new CreatePurchaseOutput(PurchaseOrderResponse.From(order), persisted.Created);
        }
        catch (SupplierGatewayException ex) when (ex.Code is "supplier_identity_conflict" or "supplier_business_rejection")
        {
            throw;
        }
        catch (SupplierGatewayException)
        {
            var order = await submission.MarkUnknownAsync(persisted.Order.Id, CancellationToken.None);
            return new CreatePurchaseOutput(PurchaseOrderResponse.From(order), persisted.Created);
        }
        catch (OperationCanceledException) when (cancellationToken.IsCancellationRequested)
        {
            await submission.MarkUnknownAsync(persisted.Order.Id, CancellationToken.None);
            throw;
        }
    }
}

/// <summary>以原路徑查單並保留已確定結果的入站用例。</summary>
public sealed class ReconcilePurchaseUseCase(IPurchaseOrderRepository repository,
    IPurchaseSubmissionCommitter submission, ISupplierGateway supplier)
    : IOperationUseCase<ReconcilePurchaseInput, PurchaseOrderResponse>
{
    /// <inheritdoc />
    public async Task<PurchaseOrderResponse> ExecuteAsync(ReconcilePurchaseInput input, CancellationToken cancellationToken)
    {
        var order = await repository.FindByIdAsync(input.PurchaseOrderId, cancellationToken)
            ?? throw new ProcurementRuleException("purchase_not_found", "Purchase order was not found.");
        try
        {
            var found = await supplier.LookupAsync(order.Identity, cancellationToken);
            if (found.Kind == SupplierLookupKind.Found && found.Outcome is not null)
                return PurchaseOrderResponse.From(await submission.ApplyOutcomeAsync(order.Id, found.Outcome, cancellationToken));
            return PurchaseOrderResponse.From(order.State is PurchaseOrderState.PendingSubmission or PurchaseOrderState.SubmissionUnknown
                ? await submission.MarkUnknownAsync(order.Id, cancellationToken) : order);
        }
        catch (SupplierGatewayException ex) when (ex.Code == "supplier_identity_conflict" ||
            ex.Code == "supplier_invalid_response" &&
            order.State is not (PurchaseOrderState.PendingSubmission or PurchaseOrderState.SubmissionUnknown))
        {
            throw;
        }
        catch (SupplierGatewayException)
        {
            return PurchaseOrderResponse.From(order.State is PurchaseOrderState.PendingSubmission or PurchaseOrderState.SubmissionUnknown
                ? await submission.MarkUnknownAsync(order.Id, CancellationToken.None) : order);
        }
    }
}

/// <summary>登錄實際收到的貨品並產生同交易來源事件。</summary>
public sealed class ReceiveGoodsUseCase(IGoodsReceiptCommitter committer)
    : IOperationUseCase<ReceiveGoodsInput, ReceiveGoodsOutput>
{
    /// <inheritdoc />
    public async Task<ReceiveGoodsOutput> ExecuteAsync(ReceiveGoodsInput input, CancellationToken cancellationToken)
    {
        if (input.ReceiptId == Guid.Empty || input.Quantity <= 0)
            throw new ProcurementRuleException("invalid_receipt", "ReceiptId and positive quantity are required.");
        var committed = await committer.CommitAsync(input.PurchaseOrderId, input.ReceiptId, order =>
        {
            var prior = order.Receipts.FirstOrDefault(x => x.ReceiptId == input.ReceiptId);
            var receipt = order.Receive(input.ReceiptId, input.Quantity, DateTimeOffset.UtcNow);
            return new ReceiptCommitResult(order, receipt, prior is null);
        }, cancellationToken);
        return new ReceiveGoodsOutput(PurchaseOrderResponse.From(committed.Order),
            GoodsReceiptResponse.From(committed.Receipt), committed.Created);
    }
}
