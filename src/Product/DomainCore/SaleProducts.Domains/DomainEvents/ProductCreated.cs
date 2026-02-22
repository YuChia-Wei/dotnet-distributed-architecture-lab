using Lab.BuildingBlocks.Domains;

namespace SaleProducts.Domains.DomainEvents;

public sealed record ProductCreated(Guid ProductId, string Name, decimal Price, DateTime OccurredOn) : IDomainEvent
{
    public Guid EventId { get; init; } = Guid.NewGuid();
}