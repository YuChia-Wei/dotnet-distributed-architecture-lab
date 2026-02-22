# ADR-031: Reactor 介面必須使用 DomainEventData (.NET)

## 狀態
Accepted (2025-08-19)

## 背景
Reactor 介面若使用 `DomainEvent`（或未指定泛型）會導致與事件匯流排型別不一致。為保持框架一致性，Reactor 必須接收 `DomainEventData`。

## 決策
所有 Reactor 介面必須繼承 `IReactor<DomainEventData>`。

### 正確寫法
```csharp
public interface INotifyProductBacklogItemWhenSprintStartedReactor
    : IReactor<DomainEventData>
{
}
```

### 錯誤寫法
```csharp
// ❌ 使用 DomainEvent
public interface INotifyPbiReactor : IReactor<DomainEvent> { }

// ❌ 缺少泛型
public interface INotifyPbiReactor : IReactor { }
```

## 理由
1. **框架相容性**：Message Bus 發布的是 `DomainEventData`
2. **型別安全**：編譯期即可發現錯誤
3. **一致性**：所有事件都走 `DomainEventData`

## 實作要點

### Reactor Interface
```csharp
public interface INotifyProductBacklogItemWhenSprintStartedReactor
    : IReactor<DomainEventData>
{
}
```

### Service Implementation
```csharp
public class NotifyProductBacklogItemWhenSprintStartedService
    : INotifyProductBacklogItemWhenSprintStartedReactor
{
    public Task Handle(DomainEventData eventData)
    {
        var domainEvent = DomainEventMapper.ToDomainEvent(eventData);
        if (domainEvent is SprintStarted)
        {
            // handle
        }
        return Task.CompletedTask;
    }
}
```

## 檢查點
- [ ] Reactor 介面必須是 `IReactor<DomainEventData>`
- [ ] Handler 接收 `DomainEventData`
- [ ] 先轉換為 DomainEvent 再處理

