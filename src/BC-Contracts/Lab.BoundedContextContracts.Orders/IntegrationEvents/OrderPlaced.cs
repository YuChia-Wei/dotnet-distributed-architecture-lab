using Lab.BuildingBlocks.Integrations;

using System.Text.Json.Serialization;

namespace Lab.BoundedContextContracts.Orders.IntegrationEvents;

/// <summary>
/// 下單完成的 integration event
/// </summary>
public record OrderPlaced : IIntegrationEvent
{
    /// <summary>
    /// 下單完成的 integration event
    /// </summary>
    /// <param name="orderId">訂單的唯一識別碼</param>
    /// <param name="productId"></param>
    /// <param name="productName">產品名稱</param>
    /// <param name="quantity">訂購數量</param>
    public OrderPlaced(Guid orderId, Guid productId, string productName, int quantity)
        : this(orderId, productId, productName, quantity, DateTime.UtcNow)
    {
    }

    /// <summary>使用已儲存的發生時間重建下單完成事件。</summary>
    /// <param name="orderId">訂單識別碼。</param>
    /// <param name="productId">產品識別碼。</param>
    /// <param name="productName">產品名稱。</param>
    /// <param name="quantity">訂購數量。</param>
    /// <param name="occurredOn">原始事件發生時間。</param>
    [JsonConstructor]
    public OrderPlaced(Guid orderId, Guid productId, string productName, int quantity, DateTime occurredOn)
    {
        this.OccurredOn = occurredOn;
        this.OrderId = orderId;
        this.ProductId = productId;
        this.ProductName = productName;
        this.Quantity = quantity;
    }

    public Guid ProductId { get; set; }

    /// <summary>
    /// 訂單的唯一識別碼
    /// </summary>
    public Guid OrderId { get; }

    /// <summary>
    /// 產品名稱
    /// </summary>
    public string ProductName { get; }

    /// <summary>
    /// 訂購數量
    /// </summary>
    public int Quantity { get; }

    /// <summary>
    /// 發生時間
    /// </summary>
    public DateTime OccurredOn { get; }
}
