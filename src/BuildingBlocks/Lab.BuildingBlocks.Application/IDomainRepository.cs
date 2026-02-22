using Lab.BuildingBlocks.Domains;

namespace Lab.BuildingBlocks.Application;

/// <summary>
/// 領域 Repository 介面
/// 提供聚合根的持久化操作，僅包含標準 CRUD 方法
/// </summary>
/// <typeparam name="TEntity">聚合根類型</typeparam>
/// <typeparam name="TId">聚合根識別碼類型</typeparam>
public interface IDomainRepository<TEntity, in TId> where TEntity : IAggregateRoot<TId> where TId : notnull
{
    /// <summary>
    /// 依識別碼查詢聚合根，若不存在則回傳 null
    /// </summary>
    /// <param name="id">聚合根識別碼</param>
    /// <param name="cancellationToken">取消操作的權杖</param>
    /// <returns>查詢到的聚合根，或 null</returns>
    Task<TEntity?> FindByIdAsync(TId id, CancellationToken cancellationToken = default);

    /// <summary>
    /// 依多個識別碼批次查詢聚合根
    /// </summary>
    /// <param name="ids">聚合根識別碼集合</param>
    /// <param name="cancellationToken">取消操作的權杖</param>
    /// <returns>查詢到的聚合根集合</returns>
    Task<IEnumerable<TEntity>> FindByIdsAsync(IEnumerable<TId> ids, CancellationToken cancellationToken = default);

    /// <summary>
    /// 儲存聚合根（新增或更新）
    /// </summary>
    /// <param name="entity">要儲存的聚合根</param>
    /// <param name="cancellationToken">取消操作的權杖</param>
    Task SaveAsync(TEntity entity, CancellationToken cancellationToken = default);

    /// <summary>
    /// 批次儲存多個聚合根
    /// </summary>
    /// <param name="entities">要儲存的聚合根集合</param>
    /// <param name="cancellationToken">取消操作的權杖</param>
    Task SaveAllAsync(IEnumerable<TEntity> entities, CancellationToken cancellationToken = default);

    /// <summary>
    /// 刪除聚合根
    /// </summary>
    /// <param name="entity">要刪除的聚合根</param>
    /// <param name="cancellationToken">取消操作的權杖</param>
    Task DeleteAsync(TEntity entity, CancellationToken cancellationToken = default);
}