using Lab.BuildingBlocks.Domains;

namespace SaleProducts.Domains.DomainEvents;

public record ProductUpdated(Guid ProductId, string Name, string Description, decimal Price, int Stock, DateTime OccurredOn) : IDomainEvent;