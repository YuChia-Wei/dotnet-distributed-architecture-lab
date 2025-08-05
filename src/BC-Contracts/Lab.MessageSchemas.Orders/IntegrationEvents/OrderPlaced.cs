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
    /// <param name="OrderId">訂單的唯一識別碼</param>
    /// <param name="ProductName">產品名稱</param>
    /// <param name="Quantity">訂購數量</param>
    public OrderPlaced(Guid OrderId, string ProductName, int Quantity)
    {
        this.OccurredOn = DateTime.UtcNow;
        this.OrderId = OrderId;
        this.ProductName = ProductName;
        this.Quantity = Quantity;
    }

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