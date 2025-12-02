using Lab.BuildingBlocks.Integrations;

namespace Lab.BoundedContextContracts.Orders.IntegrationEvents;

/// <summary>
/// 訂單已完成交付的 integration event
/// </summary>
public record OrderDelivered : IIntegrationEvent
{
    /// <summary>
    /// 訂單已完成交付的 integration event
    /// </summary>
    /// <param name="orderId">訂單識別碼</param>
    public OrderDelivered(Guid orderId)
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
