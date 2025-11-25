using System;
using System.Threading.Tasks;
using InventoryControl.Applications.Dtos;
using InventoryControl.Applications.Repositories;
using InventoryControl.Domains;

namespace InventoryControl.Applications.Commands;

public record InitProductStockRequestCommand(Guid ProductId, int Stock);

public class InitProductStockRequestCommandHandler
{
    public static async Task<InitProductStockResultDto> HandleAsync(
        InitProductStockRequestCommand command,
        IInventoryItemDomainRepository repository)
    {
        var inventoryItem = await repository.GetByProductIdAsync(command.ProductId);

        if (inventoryItem != null)
        {
            return new InitProductStockResultDto
            {
                IsSuccess = false,
                CurrentStock = inventoryItem.Stock,
                ErrorMessage = "InventoryItemAlreadyExists"
            };
        }

        var item = new InventoryItem(command.ProductId, command.Stock);

        await repository.AddAsync(item);

        return new InitProductStockResultDto
        {
            IsSuccess = true,
            CurrentStock = item.Stock
        };
    }
}