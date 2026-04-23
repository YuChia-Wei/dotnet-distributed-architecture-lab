using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using InventoryControl.Applications.Repositories;

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
    Task<GetInventoryItemAvailableQuantityOutput> ExecuteAsync(GetInventoryItemAvailableQuantityInput input, CancellationToken cancellationToken = default);
}

/// <summary>
/// 取得可用庫存數量 use case 的預設實作。
/// </summary>
public class GetInventoryItemAvailableQuantityUseCase(IInventoryItemDomainRepository repository) : IGetInventoryItemAvailableQuantityUseCase
{
    /// <summary>
    /// 執行取得可用庫存數量 use case。
    /// </summary>
    /// <param name="input">查詢庫存所需的輸入資料。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    /// <returns>可用庫存結果。</returns>
    public Task<GetInventoryItemAvailableQuantityOutput> ExecuteAsync(
        GetInventoryItemAvailableQuantityInput input,
        CancellationToken cancellationToken = default)
    {
        return HandleAsync(input, repository, cancellationToken);
    }

    /// <summary>
    /// 執行取得可用庫存數量核心流程。
    /// </summary>
    /// <param name="input">查詢庫存所需的輸入資料。</param>
    /// <param name="repository">庫存領域儲存庫。</param>
    /// <returns>可用庫存結果。</returns>
    public static async Task<GetInventoryItemAvailableQuantityOutput> HandleAsync(
        GetInventoryItemAvailableQuantityInput input,
        IInventoryItemDomainRepository repository,
        CancellationToken cancellationToken = default)
    {
        var inventoryItem = await repository.GetByProductIdAsync(input.ProductId);

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
