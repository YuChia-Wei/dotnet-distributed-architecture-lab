using Lab.BuildingBlocks.Domains;

namespace SaleOrders.Domains.DomainEvents;

/// <summary>
/// 訂單已完成交付之領域事件
/// </summary>
public record OrderDeliveredDomainEvent(Guid OrderId, DateTime OccurredOn) : IDomainEvent;