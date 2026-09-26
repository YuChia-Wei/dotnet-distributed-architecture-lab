using System.Text.Json.Serialization;

namespace Lab.BoundedContextContracts.Procurement.IntegrationEvents;

/// <summary>採購端擁有的 v1 實際收貨事實；ReceiptId 是重送時不變的訊息識別碼。</summary>
public sealed record GoodsReceived
{
    /// <summary>建立有效的實際收貨事件。</summary>
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

    /// <summary>全域收貨與訊息識別碼。</summary>
    [JsonPropertyName("receiptId")]
    public Guid ReceiptId { get; }
    /// <summary>來源採購單識別碼。</summary>
    [JsonPropertyName("purchaseOrderId")]
    public Guid PurchaseOrderId { get; }
    /// <summary>既有商品識別碼。</summary>
    [JsonPropertyName("productId")]
    public Guid ProductId { get; }
    /// <summary>實際收到的正整數數量。</summary>
    [JsonPropertyName("quantity")]
    public int Quantity { get; }
    /// <summary>收貨發生時間。</summary>
    [JsonPropertyName("receivedAt")]
    public DateTimeOffset ReceivedAt { get; }
}
