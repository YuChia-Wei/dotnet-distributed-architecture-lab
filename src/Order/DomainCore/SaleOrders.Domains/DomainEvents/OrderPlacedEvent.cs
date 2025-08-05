using Lab.BuildingBlocks.Domains;

namespace SaleOrders.Domains.DomainEvents;

public record OrderPlacedEvent(Guid OrderId, DateTime OrderDate, decimal TotalAmount, string ProductName, int Quantity, DateTime OccurredOn)
    : IDomainEvent;