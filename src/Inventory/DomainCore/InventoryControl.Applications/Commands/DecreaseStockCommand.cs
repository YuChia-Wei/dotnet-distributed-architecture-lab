using System;
using System.Threading.Tasks;
using InventoryControl.Applications.Dtos;
using InventoryControl.Applications.Repositories;
using Lab.BoundedContextContracts.Inventory.IntegrationEvents;
using Lab.BuildingBlocks.Integrations;

namespace InventoryControl.Applications.Commands;

/// <summary>
/// 扣除庫存命令
/// </summary>
public record DecreaseStockCommand
{
    /// <summary>
    /// 扣除庫存命令
    /// </summary>
    /// <param name="productId"></param>
    /// <param name="Quantity"></param>
    public DecreaseStockCommand(Guid productId, int Quantity)
    {
        this.ProductId = productId;
        this.Quantity = Quantity;
    }

    public Guid ProductId { get; set; }

    public int Quantity { get; init; }
}

/// <summary>
/// 扣除庫存命令處理器
/// </summary>
public class DecreaseStockCommandHandler
{
    /// <summary>
    /// 處理命令
    /// </summary>
    /// <param name="command">扣除庫存命令</param>
    /// <param name="repository">訂單領域儲存庫</param>
    /// <param name="publisher"></param>
    /// <returns>新建訂單的識別碼</returns>
    public static async Task<DecreaseStockResultDto> HandleAsync(
        DecreaseStockCommand command,
        IInventoryItemDomainRepository repository,
        IIntegrationEventPublisher publisher)
    {
        var inventoryItem = await repository.GetByProductIdAsync(command.ProductId);
        if (inventoryItem is null)
        {
            return new DecreaseStockResultDto
            {
                IsSuccess = false,
                ErrorMessage = "InventoryItemNotFound"
            };
        }

        var stockResult = inventoryItem.DecreaseStock(command.Quantity);

        if (!stockResult.IsSuccess)
        {
            return new DecreaseStockResultDto
            {
                IsSuccess = false,
                ErrorMessage = stockResult.ErrorMessage!
            };
        }

        // 正常流程：持久化 + 發整合事件(Integration Event)
        await repository.UpdateAsync(inventoryItem);

        await publisher.PublishAsync(
            new ProductStockDecreasedIntegrationEvent(
                inventoryItem.Id,
                command.ProductId,
                command.Quantity,
                inventoryItem.Stock));

        return new DecreaseStockResultDto
        {
            IsSuccess = true,
            CurrentStock = inventoryItem.Stock
        };
    }
}