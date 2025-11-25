using Lab.BuildingBlocks.Domains;

namespace SaleProducts.Domains.DomainEvents;

public record ProductCreated(Guid ProductId, string Name, decimal Price, DateTime OccurredOn) : IDomainEvent;