using Lab.BuildingBlocks.Domains;

namespace SaleOrders.Domains.DomainEvents;

public record OrderPlacedDomainEvent(
    Guid OrderId,
    DateTime OrderDate,
    decimal TotalAmount,
    Guid ProductId,
    string ProductName,
    int Quantity,
    DateTime OccurredOn)
    : IDomainEvent;