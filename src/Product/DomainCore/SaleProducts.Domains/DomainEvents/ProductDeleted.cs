using Lab.BuildingBlocks.Domains;

namespace SaleProducts.Domains.DomainEvents;

public record ProductDeleted(Guid ProductId, DateTime OccurredOn) : IDomainEvent;