using Lab.BuildingBlocks.Integrations;

namespace Lab.MessageSchemas.Orders.IntegrationEvents;

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
    {
        this.OccurredOn = DateTime.UtcNow;
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