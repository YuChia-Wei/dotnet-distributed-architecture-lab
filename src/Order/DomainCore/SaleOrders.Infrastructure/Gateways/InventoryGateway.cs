using Lab.BoundedContextContracts.Inventory.Interactions;
using SaleOrders.Applications.Gateways;
using Wolverine;

namespace SaleOrders.Infrastructure.Gateways;

public class InventoryGateway : IInventoryGateway
{
    private readonly IMessageBus _bus;

    public InventoryGateway(IMessageBus bus)
    {
        this._bus = bus;
    }

    public async Task<ReserveInventoryResponseContract> ReserveAsync(
        ReserveInventoryRequestContract requestContract,
        CancellationToken ct)
    {
        var cmd = new ReserveInventoryRequestContract
        {
            ProductId = requestContract.ProductId,
            Quantity = requestContract.Quantity
        };

        // 這裡會：
        // 1. 根據 routing 把 command 丟到 Kafka topic
        // 2. 等 Inventory 服務處理完回傳 ReserveInventoryResult
        var result = await this._bus.InvokeAsync<ReserveInventoryResponseContract>(cmd, ct);

        return result;
    }
}