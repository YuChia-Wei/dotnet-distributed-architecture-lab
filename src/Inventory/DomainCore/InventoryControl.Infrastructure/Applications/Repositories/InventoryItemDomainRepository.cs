using InventoryControl.Applications.Queries;
using InventoryControl.Applications.Repositories;
using InventoryControl.Domains;
using InventoryControl.Infrastructure.Persistence;
using Lab.BuildingBlocks.Application;
using Microsoft.EntityFrameworkCore;

namespace InventoryControl.Infrastructure.Applications.Repositories;

public sealed class InventoryItemDomainRepository(InventoryDbContext context, IDomainEventDispatcher dispatcher)
    : IInventoryItemDomainRepository, IInventoryItemQueryRepository
{
    public Task<InventoryItem?> FindByIdAsync(Guid id, CancellationToken cancellationToken = default)
        => context.InventoryItems.SingleOrDefaultAsync(item => item.Id == id, cancellationToken);

    public Task<IEnumerable<InventoryItem>> FindByIdsAsync(IEnumerable<Guid> ids, CancellationToken cancellationToken = default)
        => throw new NotImplementedException();

    public async Task SaveAsync(InventoryItem entity, CancellationToken cancellationToken = default)
    {
        try
        {
            if (context.Entry(entity).State == EntityState.Detached)
            {
                if (await context.InventoryItems.AnyAsync(item => item.Id == entity.Id, cancellationToken))
                {
                    context.InventoryItems.Attach(entity);
                    context.Entry(entity).Property(item => item.Stock).IsModified = true;
                }
                else
                {
                    context.InventoryItems.Add(entity);
                }
            }

            await context.SaveChangesAsync(cancellationToken);
        }
        catch
        {
            context.ChangeTracker.Clear();
            throw;
        }

        await dispatcher.DispatchAsync(entity.DomainEvents, cancellationToken);
    }

    public Task SaveAllAsync(IEnumerable<InventoryItem> entities, CancellationToken cancellationToken = default)
        => throw new NotImplementedException();

    public async Task DeleteAsync(InventoryItem entity, CancellationToken cancellationToken = default)
    {
        await context.InventoryItems.Where(item => item.Id == entity.Id).ExecuteDeleteAsync(cancellationToken);
        context.DetachInventoryItem(entity.Id);
    }

    public Task<InventoryItemReadModel?> FindByProductIdAsync(Guid productId, CancellationToken cancellationToken = default)
        => context.InventoryItems.AsNoTracking()
            .Where(item => item.ProductId == productId)
            .Select(item => new InventoryItemReadModel(item.Id, item.ProductId, item.Stock))
            .SingleOrDefaultAsync(cancellationToken);
}
