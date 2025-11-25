using System;
using System.Threading.Tasks;
using InventoryControl.Domains;
using Lab.BuildingBlocks.Domains;

namespace InventoryControl.Applications.Repositories;

/// <summary>
/// Represents a repository for managing Order domain entities.
/// </summary>
public interface IInventoryItemDomainRepository : IDomainRepository<InventoryItem, Guid>
{
    Task<InventoryItem?> GetByProductIdAsync(Guid productId);
}