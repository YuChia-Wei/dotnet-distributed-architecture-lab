using Lab.BuildingBlocks.Application;

namespace InventoryControl.Applications.Queries;

public sealed record InventoryItemReadModel(Guid Id, Guid ProductId, int Stock);

public interface IInventoryItemQueryRepository : IQueryRepository
{
    Task<InventoryItemReadModel?> FindByProductIdAsync(
        Guid productId,
        CancellationToken cancellationToken);
}
