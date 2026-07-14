using System;
using System.Threading.Tasks;
using InventoryControl.Applications.Repositories;
using InventoryControl.Applications.Queries;
using Lab.BuildingBlocks.Application;
using Lab.BoundedContextContracts.Inventory.IntegrationEvents;
using Lab.BuildingBlocks.Integrations;

namespace InventoryControl.Applications.UseCases;

/// <summary>
/// 增加庫存 use case 的輸入資料。
/// </summary>
public sealed class IncreaseStockInput
{
    /// <summary>
    /// 初始化增加庫存 use case 的輸入資料。
    /// </summary>
    /// <param name="productId">商品識別碼。</param>
    /// <param name="quantity">增加數量。</param>
    public IncreaseStockInput(Guid productId, int quantity)
    {
        this.ProductId = productId;
        this.Quantity = quantity;
    }

    /// <summary>
    /// 商品識別碼。
    /// </summary>
    public Guid ProductId { get; }

    /// <summary>
    /// 增加數量。
    /// </summary>
    public int Quantity { get; }
}

/// <summary>
/// 定義增加庫存 use case 的入口。
/// </summary>
public interface IIncreaseStockUseCase
{
    /// <summary>
    /// 執行增加庫存流程。
    /// </summary>
    /// <param name="input">增加庫存所需的輸入資料。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    /// <returns>進貨結果。</returns>
    Task<Result<IncreaseStockOutput>> ExecuteAsync(IncreaseStockInput input, CancellationToken cancellationToken);
}

/// <summary>
/// 增加庫存 use case 的預設實作。
/// </summary>
public class IncreaseStockUseCase(
    IInventoryItemDomainRepository repository,
    IInventoryItemQueryRepository queries,
    IIntegrationEventPublisher publisher) : IIncreaseStockUseCase
{
    /// <summary>
    /// 執行增加庫存 use case。
    /// </summary>
    /// <param name="input">增加庫存所需的輸入資料。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    /// <returns>進貨結果。</returns>
    public async Task<Result<IncreaseStockOutput>> ExecuteAsync(
        IncreaseStockInput input,
        CancellationToken cancellationToken)
    {
        var itemId = await queries.FindByProductIdAsync(input.ProductId, cancellationToken);
        var inventoryItem = itemId is null
            ? null
            : await repository.FindByIdAsync(itemId.Id, cancellationToken);
        if (inventoryItem is null)
        {
            return Result<IncreaseStockOutput>.Failure("InventoryItemNotFound");
        }

        var stockResult = inventoryItem.IncreaseStock(input.Quantity);

        if (!stockResult.IsSuccess)
        {
            return Result<IncreaseStockOutput>.Failure(stockResult.ErrorMessage!);
        }

        await repository.SaveAsync(inventoryItem, cancellationToken);

        await publisher.PublishAsync(
            new ProductStockIncreasedIntegrationEvent(
                inventoryItem.Id,
                input.ProductId,
                input.Quantity,
                inventoryItem.Stock));

        return Result<IncreaseStockOutput>.Success(new IncreaseStockOutput(inventoryItem.Stock));
    }
}

/// <summary>
/// 增加庫存 use case 的成功輸出資料。
/// </summary>
public sealed class IncreaseStockOutput
{
    /// <summary>
    /// 初始化增加庫存輸出資料。
    /// </summary>
    /// <param name="currentStock">目前庫存數量。</param>
    public IncreaseStockOutput(int currentStock)
    {
        this.CurrentStock = currentStock;
    }

    /// <summary>
    /// 目前庫存數量。
    /// </summary>
    public int CurrentStock { get; }
}
