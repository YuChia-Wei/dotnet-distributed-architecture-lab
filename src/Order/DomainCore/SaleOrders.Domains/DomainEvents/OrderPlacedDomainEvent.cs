using ArchPrecept.Contracts.Domain;

namespace SaleOrders.Domains.DomainEvents;

public sealed record OrderPlacedDomainEvent(
    Guid OrderId,
    DateTime OrderDate,
    decimal TotalAmount,
    Guid ProductId,
    string ProductName,
    int Quantity,
    DateTime OccurredOn)
    : IDomainEvent
{
    public Guid EventId { get; init; } = Guid.NewGuid();
}