using Lab.BuildingBlocks.Integrations;

using System.Text.Json.Serialization;

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
    /// <param name="reason">狀態變更原因</param>
    public OrderDelivered(Guid orderId, string reason)
        : this(orderId, reason, DateTime.UtcNow)
    {
    }

    /// <summary>使用已儲存的發生時間重建訂單交付事件。</summary>
    /// <param name="orderId">訂單識別碼。</param>
    /// <param name="reason">狀態變更原因。</param>
    /// <param name="occurredOn">原始事件發生時間。</param>
    [JsonConstructor]
    public OrderDelivered(Guid orderId, string reason, DateTime occurredOn)
    {
        this.OrderId = orderId;
        this.Reason = reason;
        this.OccurredOn = occurredOn;
    }

    /// <summary>
    /// 訂單識別碼
    /// </summary>
    public Guid OrderId { get; }

    /// <summary>狀態變更原因</summary>
    public string Reason { get; }

    /// <summary>
    /// 發生時間
    /// </summary>
    public DateTime OccurredOn { get; }
}
