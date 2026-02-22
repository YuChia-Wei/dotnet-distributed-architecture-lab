using Lab.BuildingBlocks.Domains;

namespace SaleOrders.Domains.DomainEvents;

/// <summary>
/// 訂單已取消之領域事件
/// </summary>
public sealed record OrderCancelledDomainEvent(Guid OrderId, DateTime OccurredOn) : IDomainEvent
{
    public Guid EventId { get; init; } = Guid.NewGuid();
}