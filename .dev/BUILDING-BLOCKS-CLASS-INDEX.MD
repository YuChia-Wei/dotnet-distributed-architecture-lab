# Building Blocks 實作類別索引

此文件記錄 `Lab.BuildingBlocks.Domains` 專案中**已實作**的類別與介面。
概念層完整架構設計請參考 [`.ai/BUILDING-BLOCKS-CLASS-INDEX.MD`](../.ai/BUILDING-BLOCKS-CLASS-INDEX.MD)。

---

## 核心介面

| 類別 | Namespace | 說明 |
|------|-----------|------|
| `IDomainEntity<out TId>` | `Lab.BuildingBlocks.Domains` | 領域實體介面，定義 `Id` 屬性 |
| `IAggregateRoot<out TId>` | `Lab.BuildingBlocks.Domains` | 聚合根介面，繼承 `IDomainEntity`，定義 `Version` |
| `IDomainEvent` | `Lab.BuildingBlocks.Domains` | 領域事件介面，定義 `EventId`（冪等性）與 `OccurredOn` |
| `IDomainRepository<TEntity, TId>` | `Lab.BuildingBlocks.Domains` | 領域 Repository 介面 |
| `IDomainEventDispatcher` | `Lab.BuildingBlocks.Domains` | 領域事件發送介面 |

## 基底類別

| 類別 | Namespace | 說明 |
|------|-----------|------|
| `DomainEntity<TId>` | `Lab.BuildingBlocks.Domains` | 實體基底，管理 `Id` 與 `DomainEvents` 集合 |
| `AggregateRoot<TId>` | `Lab.BuildingBlocks.Domains` | 聚合根基底，管理 `Version`（`protected set`） |
| `EsAggregateRoot<TId>` | `Lab.BuildingBlocks.Domains` | ES 聚合根基底，提供 `Apply`/`When` 模式與事件重播建構子 |

## 繼承關係

```
IDomainEntity<TId>
  └─ IAggregateRoot<TId>

DomainEntity<TId> : IDomainEntity<TId>
  └─ AggregateRoot<TId> : IAggregateRoot<TId>
       └─ EsAggregateRoot<TId>
```

## IDomainRepository 方法簽章

```csharp
public interface IDomainRepository<TEntity, in TId>
    where TEntity : IAggregateRoot<TId>
    where TId : notnull
{
    Task<TEntity?> FindByIdAsync(TId id, CancellationToken ct = default);
    Task<IEnumerable<TEntity>> FindByIdsAsync(IEnumerable<TId> ids, CancellationToken ct = default);
    Task SaveAsync(TEntity entity, CancellationToken ct = default);
    Task SaveAllAsync(IEnumerable<TEntity> entities, CancellationToken ct = default);
    Task DeleteAsync(TEntity entity, CancellationToken ct = default);
}
```

## EsAggregateRoot 使用模式

```csharp
public class Order : EsAggregateRoot<Guid>
{
    // 事件重播建構子
    public Order(IEnumerable<IDomainEvent> events) : base(events) { }

    // ORM 建構子
    public Order() { }

    // 業務方法透過 Apply 發起狀態變更
    public void Cancel()
    {
        Apply(new OrderCancelledDomainEvent(this.Id, DateTime.UtcNow));
    }

    // When 方法處理具體狀態變更
    protected override void When(IDomainEvent @event)
    {
        switch (@event)
        {
            case OrderCancelledDomainEvent:
                this.Status = OrderStatus.Cancelled;
                break;
        }
    }
}
```

## 消費此套件的 Bounded Context

| Bounded Context | Repository 介面 | 繼承 IDomainRepository |
|----------------|-----------------|----------------------|
| **InventoryControl** | `IInventoryItemDomainRepository` | ✅ `IDomainRepository<InventoryItem, Guid>` |
| **SaleOrders** | `IOrderDomainRepository` | ❌ 獨立介面（待重構） |
| **SaleProducts** | `IProductDomainRepository` | ❌ 獨立介面（待重構） |
