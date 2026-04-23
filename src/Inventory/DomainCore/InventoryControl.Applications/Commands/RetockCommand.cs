using System;
using System.Threading.Tasks;
using InventoryControl.Applications.Repositories;
using Lab.BuildingBlocks.Application;
using Lab.BoundedContextContracts.Inventory.IntegrationEvents;
using Lab.BuildingBlocks.Integrations;

namespace InventoryControl.Applications.UseCases;

/// <summary>
/// 退貨回補 use case 的輸入資料。
/// </summary>
public sealed class RestockInput
{
    /// <summary>
    /// 初始化退貨回補 use case 的輸入資料。
    /// </summary>
    /// <param name="productId">商品識別碼。</param>
    /// <param name="quantity">回補數量。</param>
    public RestockInput(Guid productId, int quantity)
    {
        this.ProductId = productId;
        this.Quantity = quantity;
    }

    /// <summary>
    /// 商品識別碼。
    /// </summary>
    public Guid ProductId { get; }

    /// <summary>
    /// 回補數量。
    /// </summary>
    public int Quantity { get; }
}

/// <summary>
/// 定義退貨回補 use case 的入口。
/// </summary>
public interface IRestockUseCase
{
    /// <summary>
    /// 執行退貨回補流程。
    /// </summary>
    /// <param name="input">退貨回補所需的輸入資料。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    /// <returns>回補結果。</returns>
    Task<Result<RestockOutput>> ExecuteAsync(RestockInput input, CancellationToken cancellationToken = default);
}

/// <summary>
/// 退貨回補 use case 的預設實作。
/// </summary>
public class RestockUseCase(
    IInventoryItemDomainRepository repository,
    IIntegrationEventPublisher publisher) : IRestockUseCase
{
    /// <summary>
    /// 執行退貨回補 use case。
    /// </summary>
    /// <param name="input">退貨回補所需的輸入資料。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    /// <returns>回補結果。</returns>
    public Task<Result<RestockOutput>> ExecuteAsync(RestockInput input, CancellationToken cancellationToken = default)
    {
        return HandleAsync(input, repository, publisher, cancellationToken);
    }

    /// <summary>
    /// 執行退貨回補核心流程。
    /// </summary>
    /// <param name="input">退貨回補所需的輸入資料。</param>
    /// <param name="repository">庫存領域儲存庫。</param>
    /// <param name="publisher">整合事件發布器。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    /// <returns>回補結果。</returns>
    public static async Task<Result<RestockOutput>> HandleAsync(
        RestockInput input,
        IInventoryItemDomainRepository repository,
        IIntegrationEventPublisher publisher,
        CancellationToken cancellationToken = default)
    {
        var inventoryItem = await repository.GetByProductIdAsync(input.ProductId);
        if (inventoryItem is null)
        {
            return Result<RestockOutput>.Failure("InventoryItemNotFound");
        }

        var stockResult = inventoryItem.Restock(input.Quantity);

        if (!stockResult.IsSuccess)
        {
            return Result<RestockOutput>.Failure(stockResult.ErrorMessage!);
        }

        await repository.SaveAsync(inventoryItem, cancellationToken);

        await publisher.PublishAsync(
            new ProductStockReturnedIntegrationEvent(
                inventoryItem.Id,
                input.ProductId,
                input.Quantity,
                inventoryItem.Stock));

        return Result<RestockOutput>.Success(new RestockOutput(inventoryItem.Stock));
    }
}

/// <summary>
/// 退貨回補 use case 的成功輸出資料。
/// </summary>
public sealed class RestockOutput
{
    /// <summary>
    /// 初始化退貨回補輸出資料。
    /// </summary>
    /// <param name="currentStock">目前庫存數量。</param>
    public RestockOutput(int currentStock)
    {
        this.CurrentStock = currentStock;
    }

    /// <summary>
    /// 目前庫存數量。
    /// </summary>
    public int CurrentStock { get; }
}
