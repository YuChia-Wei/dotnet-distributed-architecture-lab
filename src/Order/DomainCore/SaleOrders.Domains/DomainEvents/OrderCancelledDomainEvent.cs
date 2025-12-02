using Lab.BuildingBlocks.Domains;

namespace SaleOrders.Domains.DomainEvents;

/// <summary>
/// 訂單已取消之領域事件
/// </summary>
public record OrderCancelledDomainEvent(Guid OrderId, DateTime OccurredOn) : IDomainEvent;