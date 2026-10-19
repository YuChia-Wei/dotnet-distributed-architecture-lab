using ArchPrecept.Contracts.Application;
using SaleOrders.Domains;

namespace SaleOrders.Applications.Repositories;

/// <summary>Provides write-side access to the Order aggregate event stream.</summary>
public interface IOrderDomainRepository : IAggregateRepository<Order, Guid>
{
}
