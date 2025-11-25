using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using InventoryControl.Applications.Dtos;
using InventoryControl.Applications.Repositories;

namespace InventoryControl.Applications.Queries;

/// <summary>
/// 取得指定產品的庫存可用數量
/// </summary>
/// <param name="ProductId"></param>
public record GetInventoryItemAvailableQuantityQuery(Guid ProductId);

public class GetInventoryItemAvailableQuantityQueryHandler
{
    public static async Task<GetAvailableQuantityResultDto> HandleAsync(
        GetInventoryItemAvailableQuantityQuery query,
        IInventoryItemDomainRepository repository)
    {
        var inventoryItem = await repository.GetByProductIdAsync(query.ProductId);

        if (inventoryItem == null)
        {
            throw new KeyNotFoundException($"Order with ID {query.ProductId} not found.");
        }

        return new GetAvailableQuantityResultDto(inventoryItem.ProductId, inventoryItem.Stock);
    }
}