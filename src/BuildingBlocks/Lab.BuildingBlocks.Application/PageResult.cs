namespace Lab.BuildingBlocks.Application;

/// <summary>
/// 表示分頁查詢結果。
/// </summary>
/// <typeparam name="TItem">分頁項目型別。</typeparam>
public sealed class PageResult<TItem>
{
    /// <summary>
    /// 初始化分頁查詢結果。
    /// </summary>
    /// <param name="items">當前頁面的資料集合。</param>
    /// <param name="totalCount">符合條件的總筆數。</param>
    /// <param name="pageIndex">頁碼索引。</param>
    /// <param name="pageSize">每頁筆數。</param>
    public PageResult(IReadOnlyList<TItem> items, int totalCount, int pageIndex, int pageSize)
    {
        this.Items = items;
        this.TotalCount = totalCount;
        this.PageIndex = pageIndex;
        this.PageSize = pageSize;
    }

    /// <summary>
    /// 取得當前頁面的資料集合。
    /// </summary>
    public IReadOnlyList<TItem> Items { get; }

    /// <summary>
    /// 取得符合條件的總筆數。
    /// </summary>
    public int TotalCount { get; }

    /// <summary>
    /// 取得頁碼索引。
    /// </summary>
    public int PageIndex { get; }

    /// <summary>
    /// 取得每頁筆數。
    /// </summary>
    public int PageSize { get; }
}
