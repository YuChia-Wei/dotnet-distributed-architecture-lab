using ArchPrecept.Contracts.Domain;

namespace SaleProducts.Domains.DomainEvents;

public sealed record ProductUpdated(Guid ProductId, string Name, string Description, decimal Price, DateTime OccurredOn) : IDomainEvent
{
    public Guid EventId { get; init; } = Guid.NewGuid();
}