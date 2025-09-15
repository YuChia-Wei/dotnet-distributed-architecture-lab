using Lab.BuildingBlocks.Integrations;

namespace Lab.MessageSchemas.Orders.IntegrationEvents;

public record OrderCancelled(Guid OrderId) : IIntegrationEvent;