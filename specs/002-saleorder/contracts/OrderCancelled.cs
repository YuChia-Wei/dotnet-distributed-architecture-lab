using Lab.BuildingBlocks.Integrations;

namespace Lab.BoundedContextContracts.Orders.IntegrationEvents;

public record OrderCancelled(Guid OrderId) : IIntegrationEvent;