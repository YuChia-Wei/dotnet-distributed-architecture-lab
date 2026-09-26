using System.Text.RegularExpressions;

namespace Procurement.Domains;

public enum PurchaseOrderState { PendingSubmission, SubmissionUnknown, Accepted, Rejected, PartiallyReceived, Received }

public sealed class ProcurementRuleException(string code, string message) : Exception(message)
{
    public string Code { get; } = code;
}

public sealed record PurchaseIdentity(Guid ClientRequestId, Guid ProductId, string SupplierSku,
    int Quantity, decimal UnitPrice, string Currency, string Provider)
{
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

public sealed record GoodsReceipt(Guid ReceiptId, Guid PurchaseOrderId, Guid ProductId,
    int Quantity, DateTimeOffset ReceivedAt);

public sealed class PurchaseOrder
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

    public Guid Id { get; }
    public PurchaseIdentity Identity { get; }
    public PurchaseOrderState State { get; private set; }
    public string? SupplierOrderId { get; private set; }
    public int ReceivedQuantity { get; private set; }
    public int Version { get; private set; }
    public DateTimeOffset CreatedAt { get; }
    public DateTimeOffset UpdatedAt { get; private set; }
    public IReadOnlyList<GoodsReceipt> Receipts => receipts.AsReadOnly();

    public static PurchaseOrder Create(Guid id, PurchaseIdentity identity, DateTimeOffset now)
    {
        identity.Validate();
        if (id == Guid.Empty) throw new ProcurementRuleException("invalid_identity", "PurchaseOrderId is required.");
        return new PurchaseOrder(id, identity, PurchaseOrderState.PendingSubmission, null, 0, 0, now, now, []);
    }

    public static PurchaseOrder Restore(Guid id, PurchaseIdentity identity, PurchaseOrderState state,
        string? supplierOrderId, int receivedQuantity, int version, DateTimeOffset createdAt,
        DateTimeOffset updatedAt, IEnumerable<GoodsReceipt> receipts) =>
        new(id, identity, state, supplierOrderId, receivedQuantity, version, createdAt, updatedAt, receipts);

    public void RequireIdentity(PurchaseIdentity identity)
    {
        if (Identity != identity)
            throw new ProcurementRuleException("purchase_identity_conflict", "ClientRequestId already belongs to a different purchase.");
    }

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

    public void MarkUnknown(DateTimeOffset now)
    {
        if (State is not (PurchaseOrderState.PendingSubmission or PurchaseOrderState.SubmissionUnknown)) return;
        State = PurchaseOrderState.SubmissionUnknown;
        UpdatedAt = now;
        Version++;
    }

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
