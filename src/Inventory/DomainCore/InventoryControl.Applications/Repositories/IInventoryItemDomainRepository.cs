using InventoryControl.Domains;
using ArchPrecept.Contracts.Application;
using ArchPrecept.Contracts.Domain;

namespace InventoryControl.Applications.Repositories;

/// <summary>
/// 庫存項目 Repository 介面
/// </summary>
public interface IInventoryItemDomainRepository : IDomainRepository<InventoryItem, Guid>
{
}
