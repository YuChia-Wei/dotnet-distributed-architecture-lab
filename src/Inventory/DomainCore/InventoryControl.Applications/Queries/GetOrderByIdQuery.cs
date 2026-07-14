using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using InventoryControl.Applications.Queries;

namespace InventoryControl.Applications.UseCases;

/// <summary>
/// 取得可用庫存數量 use case 的輸入資料。
/// </summary>
public sealed class GetInventoryItemAvailableQuantityInput
{
    /// <summary>
    /// 初始化取得可用庫存數量 use case 的輸入資料。
    /// </summary>
    /// <param name="productId">商品識別碼。</param>
    public GetInventoryItemAvailableQuantityInput(Guid productId)
    {
        this.ProductId = productId;
    }

    /// <summary>
    /// 商品識別碼。
    /// </summary>
    public Guid ProductId { get; }
}

/// <summary>
/// 定義取得可用庫存數量 use case 的入口。
/// </summary>
public interface IGetInventoryItemAvailableQuantityUseCase
{
    /// <summary>
    /// 取得指定商品的可用庫存數量。
    /// </summary>
    /// <param name="input">查詢庫存所需的輸入資料。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    /// <returns>可用庫存結果。</returns>
    Task<GetInventoryItemAvailableQuantityOutput> ExecuteAsync(
        GetInventoryItemAvailableQuantityInput input,
        CancellationToken cancellationToken);
}

/// <summary>
/// 取得可用庫存數量 use case 的預設實作。
/// </summary>
public class GetInventoryItemAvailableQuantityUseCase(IInventoryItemQueryRepository repository) : IGetInventoryItemAvailableQuantityUseCase
{
    /// <summary>
    /// 執行取得可用庫存數量 use case。
    /// </summary>
    /// <param name="input">查詢庫存所需的輸入資料。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    /// <returns>可用庫存結果。</returns>
    public async Task<GetInventoryItemAvailableQuantityOutput> ExecuteAsync(
        GetInventoryItemAvailableQuantityInput input,
        CancellationToken cancellationToken)
    {
        var inventoryItem = await repository.FindByProductIdAsync(input.ProductId, cancellationToken);

        if (inventoryItem == null)
        {
            throw new KeyNotFoundException($"Order with ID {input.ProductId} not found.");
        }

        return new GetInventoryItemAvailableQuantityOutput(inventoryItem.ProductId, inventoryItem.Stock);
    }
}

/// <summary>
/// 取得可用庫存數量 use case 的輸出資料。
/// </summary>
public sealed class GetInventoryItemAvailableQuantityOutput
{
    /// <summary>
    /// 初始化可用庫存輸出資料。
    /// </summary>
    /// <param name="productId">商品識別碼。</param>
    /// <param name="availableStock">可用庫存數量。</param>
    public GetInventoryItemAvailableQuantityOutput(Guid productId, int availableStock)
    {
        this.ProductId = productId;
        this.AvailableStock = availableStock;
    }

    /// <summary>
    /// 商品識別碼。
    /// </summary>
    public Guid ProductId { get; }

    /// <summary>
    /// 可用庫存數量。
    /// </summary>
    public int AvailableStock { get; }
}
