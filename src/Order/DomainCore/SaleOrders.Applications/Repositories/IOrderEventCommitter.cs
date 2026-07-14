using Lab.BuildingBlocks.Integrations;
using SaleOrders.Domains;

namespace SaleOrders.Applications.Repositories;

/// <summary>Commits Order events and their outgoing integration events as one unit.</summary>
public interface IOrderEventCommitter
{
    /// <summary>Atomically appends pending aggregate events and records outgoing messages.</summary>
    Task CommitAsync(
        Order order,
        IReadOnlyCollection<IIntegrationEvent> integrationEvents,
        CancellationToken cancellationToken);
}
