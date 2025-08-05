namespace Lab.BuildingBlocks.Domains;

/// <summary>
/// 領域事件發布者
/// </summary>
/// <remarks>
/// Dispatch 強調「路由 / 分派」到同步或極低延遲的本地 Handler；多半走 Mediator 或類似模式，行為接近函式呼叫。
/// </remarks>
public interface IDomainEventDispatcher
{
    /// <summary>
    /// 發布領域事件
    /// </summary>
    /// <param name="events"></param>
    /// <param name="ct"></param>
    /// <returns></returns>
    Task DispatchAsync(IEnumerable<IDomainEvent> events, CancellationToken ct = default);
}