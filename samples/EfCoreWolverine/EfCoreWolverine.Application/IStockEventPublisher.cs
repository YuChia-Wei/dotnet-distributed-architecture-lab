using Lab.BoundedContextContracts.Inventory.IntegrationEvents;

namespace EfCoreWolverine.Application;

/// <summary>
/// Records an outgoing integration event in the current processing transaction.
/// Completion means the event is staged, not that a broker has received it.
/// </summary>
public interface IStockEventPublisher
{
    Task PublishAsync(
        ProductStockDecreasedIntegrationEvent integrationEvent,
        CancellationToken cancellationToken);
}
