# ADR-035: Transaction Outbox Pattern 實作策略 (.NET)

## 狀態
已接受 (Accepted)

## 背景
事件驅動架構需要確保：
1. 事件不遺失
2. 全域順序
3. 事件溯源
4. 依 Aggregate 查詢事件歷史

## 決策

### 1. InMemory Outbox 實作位置
- **實作於**: `GenericInMemoryRepository`
- **原因**: Repository 保存 aggregate 的同時保存事件最自然

### 2. Outbox 資料結構
```csharp
private readonly ConcurrentDictionary<string, List<OutboxEntry>> _outbox = new();
private long _globalIndex;

private sealed record OutboxEntry(InternalDomainEvent Event, long GlobalIndex, string StreamName);
```

### 3. Stream Name 格式
- **格式**: `{AggregateType}:{AggregateId}`
- **範例**: `Product:product-001`

### 4. 事件儲存時機
```csharp
public void Save(T aggregate)
{
    _store[aggregate.Id] = aggregate;
    StoreEventsInOutbox(aggregate);
    PublishEvents(aggregate);
    aggregate.ClearDomainEvents();
}
```

### 5. 查詢介面
```csharp
public IReadOnlyList<InternalDomainEvent> FindByStreamName(string streamName);
public IReadOnlyList<InternalDomainEvent> GetAllDomainEvents();
```

## 影響
### 正面影響
- 事件不會遺失
- 支援事件重播
- 全域順序

### 負面影響
- 記憶體增加
- InMemory 於重啟後遺失

## 未來改進
1. 使用 EF Core + WolverineFx Outbox 持久化
2. 事件快照
3. 事件壓縮/清理

## 參考資料
- Transactional Outbox Pattern
