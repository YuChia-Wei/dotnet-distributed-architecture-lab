using InventoryControl.Domains;
using Lab.BuildingBlocks.Application;
using Microsoft.EntityFrameworkCore;

namespace EfCoreWolverine.Infrastructure;

public sealed class EfInventoryRepository(InventoryDbContext db)
    : IAggregateRepository<InventoryItem, Guid>
{
    public Task<InventoryItem?> FindByIdAsync(Guid id, CancellationToken cancellationToken = default)
        => db.InventoryItems.SingleOrDefaultAsync(x => x.Id == id, cancellationToken);

    /// <summary>
    /// Registers the already-tracked aggregate. Does NOT call SaveChanges or commit.
    /// Wolverine saves the shared context and completes the inbox in the same transaction.
    /// </summary>
    public Task SaveAsync(InventoryItem aggregate, CancellationToken cancellationToken = default)
    {
        cancellationToken.ThrowIfCancellationRequested();
        if (db.Entry(aggregate).State == EntityState.Detached)
            throw new InvalidOperationException("Load the aggregate through this scoped repository before saving.");

        db.ChangeTracker.DetectChanges();
        return Task.CompletedTask;
    }
}
