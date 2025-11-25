using Lab.BoundedContextContracts.Inventory.Interactions;

namespace SaleOrders.Applications.Gateways;

public interface IInventoryGateway
{
    Task<ReserveInventoryResponseContract> ReserveAsync(
        ReserveInventoryRequestContract request,
        CancellationToken ct);
}