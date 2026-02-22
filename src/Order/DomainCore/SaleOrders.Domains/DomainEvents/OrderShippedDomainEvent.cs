using Lab.BuildingBlocks.Domains;

namespace SaleOrders.Domains.DomainEvents;

/// <summary>
/// 訂單已出貨之領域事件
/// </summary>
public sealed record OrderShippedDomainEvent(Guid OrderId, DateTime OccurredOn) : IDomainEvent
{
    public Guid EventId { get; init; } = Guid.NewGuid();
}