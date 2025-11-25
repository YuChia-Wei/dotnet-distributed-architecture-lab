using System;
using System.Threading.Tasks;
using InventoryControl.Applications.Dtos;
using InventoryControl.Applications.Repositories;
using Lab.BoundedContextContracts.Inventory.IntegrationEvents;
using Lab.BuildingBlocks.Integrations;

namespace InventoryControl.Applications.Commands;

/// <summary>
/// 增加庫存命令
/// </summary>
public record IncreaseStockCommand
{
    /// <summary>
    /// 增加庫存命令
    /// </summary>
    /// <param name="productId"></param>
    /// <param name="Quantity"></param>
    public IncreaseStockCommand(Guid productId, int Quantity)
    {
        this.ProductId = productId;
        this.Quantity = Quantity;
    }

    public Guid ProductId { get; set; }

    public int Quantity { get; init; }
}

/// <summary>
/// 增加庫存命令處理器
/// </summary>
public class IncreaseStockCommandHandler
{
    /// <summary>
    /// 處理命令
    /// </summary>
    /// <param name="command">增加庫存命令</param>
    /// <param name="repository">訂單領域儲存庫</param>
    /// <param name="publisher"></param>
    /// <returns>新建訂單的識別碼</returns>
    public static async Task<IncreaseStockResultDto> HandleAsync(
        IncreaseStockCommand command,
        IInventoryItemDomainRepository repository,
        IIntegrationEventPublisher publisher)
    {
        var inventoryItem = await repository.GetByProductIdAsync(command.ProductId);
        if (inventoryItem is null)
        {
            return new IncreaseStockResultDto
            {
                IsSuccess = false,
                ErrorMessage = "InventoryItemNotFound"
            };
        }

        var stockResult = inventoryItem.IncreaseStock(command.Quantity);

        if (!stockResult.IsSuccess)
        {
            return new IncreaseStockResultDto
            {
                IsSuccess = false,
                ErrorMessage = stockResult.ErrorMessage!
            };
        }

        // 正常流程：持久化 + 發整合事件(Integration Event)
        await repository.UpdateAsync(inventoryItem);

        await publisher.PublishAsync(
            new ProductStockIncreasedIntegrationEvent(
                inventoryItem.Id,
                command.ProductId,
                command.Quantity,
                inventoryItem.Stock));

        return new IncreaseStockResultDto
        {
            IsSuccess = true,
            CurrentStock = inventoryItem.Stock
        };
    }
}