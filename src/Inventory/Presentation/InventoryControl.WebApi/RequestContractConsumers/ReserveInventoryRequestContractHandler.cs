using System.Threading.Tasks;
using InventoryControl.Applications.Commands;
using InventoryControl.Applications.Dtos;
using Lab.BoundedContextContracts.Inventory.Interactions;
using Wolverine;

namespace InventoryControl.WebApi.RequestContractConsumers;

public class ReserveInventoryRequestContractHandler
{
    private readonly IMessageBus _bus;

    public ReserveInventoryRequestContractHandler(IMessageBus bus)
    {
        this._bus = bus;
    }

    public async Task<ReserveInventoryResponseContract> HandleAsync(ReserveInventoryRequestContract request)
    {
        var resultDto = await this._bus.InvokeAsync<DecreaseStockResultDto>(new DecreaseStockCommand(request.ProductId, request.Quantity));
        return new ReserveInventoryResponseContract
        {
            Result = resultDto.IsSuccess
        };
    }
}