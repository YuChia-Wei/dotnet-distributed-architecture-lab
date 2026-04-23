using System;
using System.Threading.Tasks;
using InventoryControl.Applications.Repositories;
using InventoryControl.Domains;
using Lab.BuildingBlocks.Application;

namespace InventoryControl.Applications.UseCases;

/// <summary>
/// 初始化商品庫存 use case 的輸入資料。
/// </summary>
public sealed class InitProductStockInput
{
    /// <summary>
    /// 初始化商品庫存 use case 的輸入資料。
    /// </summary>
    /// <param name="productId">商品識別碼。</param>
    /// <param name="stock">初始庫存數量。</param>
    public InitProductStockInput(Guid productId, int stock)
    {
        this.ProductId = productId;
        this.Stock = stock;
    }

    /// <summary>
    /// 商品識別碼。
    /// </summary>
    public Guid ProductId { get; }

    /// <summary>
    /// 初始庫存數量。
    /// </summary>
    public int Stock { get; }
}

/// <summary>
/// 定義初始化商品庫存 use case 的入口。
/// </summary>
public interface IInitProductStockUseCase
{
    /// <summary>
    /// 初始化指定商品的庫存資料。
    /// </summary>
    /// <param name="input">初始化庫存所需的輸入資料。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    /// <returns>初始化庫存結果。</returns>
    Task<Result<InitProductStockOutput>> ExecuteAsync(InitProductStockInput input, CancellationToken cancellationToken = default);
}

/// <summary>
/// 初始化商品庫存 use case 的預設實作。
/// </summary>
public class InitProductStockUseCase(IInventoryItemDomainRepository repository) : IInitProductStockUseCase
{
    /// <summary>
    /// 執行初始化商品庫存 use case。
    /// </summary>
    /// <param name="input">初始化庫存所需的輸入資料。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    /// <returns>初始化庫存結果。</returns>
    public Task<Result<InitProductStockOutput>> ExecuteAsync(InitProductStockInput input, CancellationToken cancellationToken = default)
    {
        return HandleAsync(input, repository, cancellationToken);
    }

    /// <summary>
    /// 執行初始化商品庫存核心流程。
    /// </summary>
    /// <param name="input">初始化庫存所需的輸入資料。</param>
    /// <param name="repository">庫存領域儲存庫。</param>
    /// <returns>初始化庫存結果。</returns>
    public static async Task<Result<InitProductStockOutput>> HandleAsync(
        InitProductStockInput input,
        IInventoryItemDomainRepository repository,
        CancellationToken cancellationToken = default)
    {
        var inventoryItem = await repository.GetByProductIdAsync(input.ProductId);

        if (inventoryItem != null)
        {
            return Result<InitProductStockOutput>.Failure("InventoryItemAlreadyExists");
        }

        var item = new InventoryItem(input.ProductId, input.Stock);

        await repository.SaveAsync(item, cancellationToken);

        return Result<InitProductStockOutput>.Success(new InitProductStockOutput(item.Stock));
    }
}

/// <summary>
/// 初始化商品庫存 use case 的成功輸出資料。
/// </summary>
public sealed class InitProductStockOutput
{
    /// <summary>
    /// 初始化商品庫存輸出資料。
    /// </summary>
    /// <param name="currentStock">目前庫存數量。</param>
    public InitProductStockOutput(int currentStock)
    {
        this.CurrentStock = currentStock;
    }

    /// <summary>
    /// 目前庫存數量。
    /// </summary>
    public int CurrentStock { get; }
}
