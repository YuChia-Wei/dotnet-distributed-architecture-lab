using Lab.BuildingBlocks.Application;

namespace SaleOrders.Applications.Queries;

/// <summary>Reads Orders query models without rehydrating aggregates.</summary>
public interface IOrderQueryRepository : IQueryRepository
{
    /// <summary>Finds an Order read model by identity.</summary>
    Task<OrderReadModel?> FindByIdAsync(
        Guid id,
        CancellationToken cancellationToken = default);

    /// <summary>Returns all Order read models.</summary>
    Task<IReadOnlyList<OrderReadModel>> FindAllAsync(
        CancellationToken cancellationToken = default);
}
