using Lab.BuildingBlocks.Integrations;

namespace Lab.BoundedContextContracts.Orders.IntegrationEvents;

/// <summary>
/// 訂單已出貨的 integration event
/// </summary>
public record OrderShipped : IIntegrationEvent
{
    /// <summary>
    /// 訂單已出貨的 integration event
    /// </summary>
    /// <param name="orderId">訂單識別碼</param>
    public OrderShipped(Guid orderId)
    {
        this.OrderId = orderId;
        this.OccurredOn = DateTime.UtcNow;
    }

    /// <summary>
    /// 訂單識別碼
    /// </summary>
    public Guid OrderId { get; }

    /// <summary>
    /// 發生時間
    /// </summary>
    public DateTime OccurredOn { get; }
}
