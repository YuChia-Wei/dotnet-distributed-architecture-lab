namespace Lab.BuildingBlocks.Domains;

/// <summary>
/// Event Sourcing 聚合根基底類別
/// 所有狀態變更必須透過 Apply/When 機制，確保事件是唯一的狀態變更來源
/// </summary>
public abstract class EsAggregateRoot<TId>
    : AggregateRoot<TId> where TId : notnull
{
    /// <summary>
    /// 事件重播用建構子
    /// </summary>
    protected EsAggregateRoot(IEnumerable<IDomainEvent> events)
    {
        foreach (var @event in events)
        {
            When(@event);
            Version++;
        }
    }

    /// <summary>
    /// ORM / 框架用無參數建構子
    /// </summary>
    protected EsAggregateRoot()
    {
    }

    /// <summary>
    /// 套用領域事件，變更聚合根狀態並記錄事件
    /// </summary>
    protected void Apply(IDomainEvent @event)
    {
        When(@event);
        AddDomainEvent(@event);
    }

    /// <summary>
    /// 根據領域事件變更聚合根內部狀態
    /// </summary>
    protected abstract void When(IDomainEvent @event);

    /// <summary>
    /// 取得最後一個領域事件
    /// </summary>
    protected IDomainEvent? GetLastDomainEvent()
        => DomainEvents.LastOrDefault();
}
