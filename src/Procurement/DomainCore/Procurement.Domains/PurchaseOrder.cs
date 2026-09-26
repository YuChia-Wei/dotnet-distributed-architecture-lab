using System.Text.RegularExpressions;

namespace Procurement.Domains;

/// <summary>採購聚合的本地識別與版本契約；此聚合不使用領域事件基底類別。</summary>
public interface IProcurementAggregateRoot
{
    /// <summary>本地聚合識別碼。</summary>
    Guid Id { get; }
    /// <summary>已提交的聚合版本。</summary>
    int Version { get; }
}

/// <summary>單品採購從送單到實際收貨的狀態。</summary>
public enum PurchaseOrderState { PendingSubmission, SubmissionUnknown, Accepted, Rejected, PartiallyReceived, Received }

/// <summary>可映射為穩定 HTTP 錯誤碼的採購業務規則例外。</summary>
public sealed class ProcurementRuleException(string code, string message) : Exception(message)
{
    /// <summary>穩定錯誤碼。</summary>
    public string Code { get; } = code;
}

/// <summary>由全域冪等鍵固定的不可變送單身分。</summary>
public sealed record PurchaseIdentity(Guid ClientRequestId, Guid ProductId, string SupplierSku,
    int Quantity, decimal UnitPrice, string Currency, string Provider)
{
    /// <summary>在任何資料庫或供應商操作前驗證所有送單欄位。</summary>
    public void Validate()
    {
        if (ClientRequestId == Guid.Empty || ProductId == Guid.Empty)
            throw new ProcurementRuleException("invalid_identity", "ClientRequestId and ProductId are required.");
        if (SupplierSku is null || SupplierSku.Length is < 1 or > 64 ||
            !Regex.IsMatch(SupplierSku, "^[A-Za-z0-9_-]+$", RegexOptions.CultureInvariant))
            throw new ProcurementRuleException("invalid_sku", "SupplierSku must contain 1–64 letters, digits, hyphens or underscores.");
        if (Quantity <= 0 || UnitPrice < 0 || UnitPrice > 9999999999999999.99m ||
            decimal.Round(UnitPrice, 2) != UnitPrice || Currency != "TWD" ||
            Provider is not ("direct" or "wiremock" or "microcks"))
            throw new ProcurementRuleException("invalid_purchase", "Quantity, price, currency or provider is invalid.");
    }
}

/// <summary>採購聚合所擁有的一筆實際收貨事實。</summary>
public sealed record GoodsReceipt(Guid ReceiptId, Guid PurchaseOrderId, Guid ProductId,
    int Quantity, DateTimeOffset ReceivedAt);

/// <summary>單品採購聚合根，負責供應商結果及收貨總量的不變條件。</summary>
public sealed class PurchaseOrder : IProcurementAggregateRoot
{
    private readonly List<GoodsReceipt> receipts;

    private PurchaseOrder(Guid id, PurchaseIdentity identity, PurchaseOrderState state,
        string? supplierOrderId, int receivedQuantity, int version, DateTimeOffset createdAt,
        DateTimeOffset updatedAt, IEnumerable<GoodsReceipt> receipts)
    {
        Id = id;
        Identity = identity;
        State = state;
        SupplierOrderId = supplierOrderId;
        ReceivedQuantity = receivedQuantity;
        Version = version;
        CreatedAt = createdAt;
        UpdatedAt = updatedAt;
        this.receipts = [..receipts];
    }

    /// <summary>本地採購單識別碼。</summary>
    public Guid Id { get; }
    /// <summary>固定的供應商送單身分。</summary>
    public PurchaseIdentity Identity { get; }
    /// <summary>目前採購與收貨狀態。</summary>
    public PurchaseOrderState State { get; private set; }
    /// <summary>供應商已確定的訂單識別碼。</summary>
    public string? SupplierOrderId { get; private set; }
    /// <summary>累計實際收貨數量。</summary>
    public int ReceivedQuantity { get; private set; }
    /// <summary>已提交的聚合版本。</summary>
    public int Version { get; private set; }
    /// <summary>本地建立時間。</summary>
    public DateTimeOffset CreatedAt { get; }
    /// <summary>最近一次狀態變更時間。</summary>
    public DateTimeOffset UpdatedAt { get; private set; }
    /// <summary>聚合持有的唯讀收貨事實。</summary>
    public IReadOnlyList<GoodsReceipt> Receipts => receipts.AsReadOnly();

    /// <summary>建立尚未向供應商確定結果的採購單。</summary>
    public static PurchaseOrder Create(Guid id, PurchaseIdentity identity, DateTimeOffset now)
    {
        identity.Validate();
        if (id == Guid.Empty) throw new ProcurementRuleException("invalid_identity", "PurchaseOrderId is required.");
        return new PurchaseOrder(id, identity, PurchaseOrderState.PendingSubmission, null, 0, 0, now, now, []);
    }

    /// <summary>由持久化欄位還原單一聚合。</summary>
    public static PurchaseOrder Restore(Guid id, PurchaseIdentity identity, PurchaseOrderState state,
        string? supplierOrderId, int receivedQuantity, int version, DateTimeOffset createdAt,
        DateTimeOffset updatedAt, IEnumerable<GoodsReceipt> receipts) =>
        new(id, identity, state, supplierOrderId, receivedQuantity, version, createdAt, updatedAt, receipts);

    /// <summary>確認相同冪等鍵沒有被重用於不同送單內容。</summary>
    public void RequireIdentity(PurchaseIdentity identity)
    {
        if (Identity != identity)
            throw new ProcurementRuleException("purchase_identity_conflict", "ClientRequestId already belongs to a different purchase.");
    }

    /// <summary>套用已驗證的供應商結果，拒絕終態回退或矛盾身分。</summary>
    public void ApplySupplierOutcome(bool accepted, string supplierOrderId, DateTimeOffset now)
    {
        if (string.IsNullOrWhiteSpace(supplierOrderId) || supplierOrderId.Length > 128)
            throw new ProcurementRuleException("supplier_identity_invalid", "SupplierOrderId is invalid.");
        if (State is PurchaseOrderState.Accepted or PurchaseOrderState.PartiallyReceived or PurchaseOrderState.Received)
        {
            if (!accepted || SupplierOrderId != supplierOrderId)
                throw new ProcurementRuleException("supplier_outcome_conflict", "Supplier outcome contradicts the accepted order.");
            return;
        }
        if (State == PurchaseOrderState.Rejected)
        {
            if (accepted || SupplierOrderId != supplierOrderId)
                throw new ProcurementRuleException("supplier_outcome_conflict", "Supplier outcome contradicts the rejected order.");
            return;
        }
        State = accepted ? PurchaseOrderState.Accepted : PurchaseOrderState.Rejected;
        SupplierOrderId = supplierOrderId;
        UpdatedAt = now;
        Version++;
    }

    /// <summary>僅將未確定的送單狀態標記為未知。</summary>
    public void MarkUnknown(DateTimeOffset now)
    {
        if (State is not (PurchaseOrderState.PendingSubmission or PurchaseOrderState.SubmissionUnknown)) return;
        State = PurchaseOrderState.SubmissionUnknown;
        UpdatedAt = now;
        Version++;
    }

    /// <summary>加入實際收貨或回傳相同識別碼的原收貨事實。</summary>
    public GoodsReceipt Receive(Guid receiptId, int quantity, DateTimeOffset now)
    {
        if (receiptId == Guid.Empty || quantity <= 0)
            throw new ProcurementRuleException("invalid_receipt", "ReceiptId and positive quantity are required.");
        var existing = receipts.SingleOrDefault(x => x.ReceiptId == receiptId);
        if (existing is not null)
        {
            if (existing.Quantity != quantity)
                throw new ProcurementRuleException("receipt_identity_conflict", "ReceiptId already has different contents.");
            return existing;
        }
        if (State is not (PurchaseOrderState.Accepted or PurchaseOrderState.PartiallyReceived))
            throw new ProcurementRuleException("receipt_state_conflict", "Only accepted orders can receive goods.");
        if (quantity > Identity.Quantity - ReceivedQuantity)
            throw new ProcurementRuleException("over_receipt", "Receipt exceeds the remaining order quantity.");
        ReceivedQuantity = checked(ReceivedQuantity + quantity);
        State = ReceivedQuantity == Identity.Quantity ? PurchaseOrderState.Received : PurchaseOrderState.PartiallyReceived;
        var receipt = new GoodsReceipt(receiptId, Id, Identity.ProductId, quantity, now);
        receipts.Add(receipt);
        UpdatedAt = now;
        Version++;
        return receipt;
    }
}
