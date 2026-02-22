using InventoryControl.Domains;
using Lab.BuildingBlocks.Application;
using Lab.BuildingBlocks.Domains;

namespace InventoryControl.Applications.Repositories;

/// <summary>
/// 庫存項目 Repository 介面
/// </summary>
public interface IInventoryItemDomainRepository : IDomainRepository<InventoryItem, Guid>
{
    Task<InventoryItem?> GetByProductIdAsync(Guid productId);
}