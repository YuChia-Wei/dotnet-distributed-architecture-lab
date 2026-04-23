using System;
using System.Threading.Tasks;
using InventoryControl.Applications.Repositories;
using Lab.BuildingBlocks.Application;
using Lab.BoundedContextContracts.Inventory.IntegrationEvents;
using Lab.BuildingBlocks.Integrations;

namespace InventoryControl.Applications.UseCases;

/// <summary>
/// 扣除庫存 use case 的輸入資料。
/// </summary>
public sealed class DecreaseStockInput
{
    /// <summary>
    /// 初始化扣除庫存 use case 的輸入資料。
    /// </summary>
    /// <param name="productId">商品識別碼。</param>
    /// <param name="quantity">扣除數量。</param>
    public DecreaseStockInput(Guid productId, int quantity)
    {
        this.ProductId = productId;
        this.Quantity = quantity;
    }

    /// <summary>
    /// 商品識別碼。
    /// </summary>
    public Guid ProductId { get; }

    /// <summary>
    /// 扣除數量。
    /// </summary>
    public int Quantity { get; }
}

/// <summary>
/// 定義扣除庫存 use case 的入口。
/// </summary>
public interface IDecreaseStockUseCase
{
    /// <summary>
    /// 執行扣除庫存流程。
    /// </summary>
    /// <param name="input">扣除庫存所需的輸入資料。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    /// <returns>扣庫結果。</returns>
    Task<Result<DecreaseStockOutput>> ExecuteAsync(DecreaseStockInput input, CancellationToken cancellationToken = default);
}

/// <summary>
/// 扣除庫存 use case 的預設實作。
/// </summary>
public class DecreaseStockUseCase(
    IInventoryItemDomainRepository repository,
    IIntegrationEventPublisher publisher) : IDecreaseStockUseCase
{
    /// <summary>
    /// 執行扣除庫存 use case。
    /// </summary>
    /// <param name="input">扣除庫存所需的輸入資料。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    /// <returns>扣庫結果。</returns>
    public Task<Result<DecreaseStockOutput>> ExecuteAsync(DecreaseStockInput input, CancellationToken cancellationToken = default)
    {
        return HandleAsync(input, repository, publisher, cancellationToken);
    }

    /// <summary>
    /// 執行扣除庫存核心流程。
    /// </summary>
    /// <param name="input">扣除庫存所需的輸入資料。</param>
    /// <param name="repository">庫存領域儲存庫。</param>
    /// <param name="publisher">整合事件發布器。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    /// <returns>扣庫結果。</returns>
    public static async Task<Result<DecreaseStockOutput>> HandleAsync(
        DecreaseStockInput input,
        IInventoryItemDomainRepository repository,
        IIntegrationEventPublisher publisher,
        CancellationToken cancellationToken = default)
    {
        var inventoryItem = await repository.GetByProductIdAsync(input.ProductId);
        if (inventoryItem is null)
        {
            return Result<DecreaseStockOutput>.Failure("InventoryItemNotFound");
        }

        var stockResult = inventoryItem.DecreaseStock(input.Quantity);

        if (!stockResult.IsSuccess)
        {
            return Result<DecreaseStockOutput>.Failure(stockResult.ErrorMessage!);
        }

        await repository.SaveAsync(inventoryItem, cancellationToken);

        await publisher.PublishAsync(
            new ProductStockDecreasedIntegrationEvent(
                inventoryItem.Id,
                input.ProductId,
                input.Quantity,
                inventoryItem.Stock));

        return Result<DecreaseStockOutput>.Success(new DecreaseStockOutput(inventoryItem.Stock));
    }
}

/// <summary>
/// 扣除庫存 use case 的成功輸出資料。
/// </summary>
public sealed class DecreaseStockOutput
{
    /// <summary>
    /// 初始化扣除庫存輸出資料。
    /// </summary>
    /// <param name="currentStock">目前庫存數量。</param>
    public DecreaseStockOutput(int currentStock)
    {
        this.CurrentStock = currentStock;
    }

    /// <summary>
    /// 目前庫存數量。
    /// </summary>
    public int CurrentStock { get; }
}
