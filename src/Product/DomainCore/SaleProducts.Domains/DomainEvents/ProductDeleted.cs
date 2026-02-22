using Lab.BuildingBlocks.Domains;

namespace SaleProducts.Domains.DomainEvents;

public sealed record ProductDeleted(Guid ProductId, DateTime OccurredOn) : IDomainEvent
{
    public Guid EventId { get; init; } = Guid.NewGuid();
}