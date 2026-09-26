using System.Text.Json.Serialization;

namespace Lab.BoundedContextContracts.Procurement.IntegrationEvents;

/// <summary>Procurement-owned v1 physical receipt fact. ReceiptId is the stable message identity.</summary>
public sealed record GoodsReceived
{
    [JsonConstructor]
    public GoodsReceived(Guid receiptId, Guid purchaseOrderId, Guid productId, int quantity, DateTimeOffset receivedAt)
    {
        if (receiptId == Guid.Empty) throw new ArgumentException("ReceiptId is required.", nameof(receiptId));
        if (purchaseOrderId == Guid.Empty) throw new ArgumentException("PurchaseOrderId is required.", nameof(purchaseOrderId));
        if (productId == Guid.Empty) throw new ArgumentException("ProductId is required.", nameof(productId));
        if (quantity <= 0) throw new ArgumentOutOfRangeException(nameof(quantity));
        ReceiptId = receiptId;
        PurchaseOrderId = purchaseOrderId;
        ProductId = productId;
        Quantity = quantity;
        ReceivedAt = receivedAt;
    }

    [JsonPropertyName("receiptId")]
    public Guid ReceiptId { get; }
    [JsonPropertyName("purchaseOrderId")]
    public Guid PurchaseOrderId { get; }
    [JsonPropertyName("productId")]
    public Guid ProductId { get; }
    [JsonPropertyName("quantity")]
    public int Quantity { get; }
    [JsonPropertyName("receivedAt")]
    public DateTimeOffset ReceivedAt { get; }
}
