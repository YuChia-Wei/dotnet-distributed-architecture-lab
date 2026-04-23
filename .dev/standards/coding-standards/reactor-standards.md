# Reactor 編碼規範 (.NET)

本文件定義 Reactor / event-driven handler 的編碼標準，包含介面型別、事件轉換、邊界責任與常見錯誤。

---

## 📌 概述

Reactor 用於：

- 處理跨 Aggregate 的事件驅動流程
- 更新 read model / archive / projection
- 觸發跨 BC 的後續協作

Reactor 不應被當成一般 command handler，也不應直接承載 controller concern。

---

## 🔴 必須遵守的規則 (MUST FOLLOW)

### 1. Reactor 介面必須使用 `DomainEventData`

所有 Reactor 介面必須繼承：

```csharp
IReactor<DomainEventData>
```

```csharp
// ✅ 正確
public interface INotifyOrderProjectionReactor : IReactor<DomainEventData>
{
}

// ❌ 錯誤：直接使用 DomainEvent
public interface INotifyOrderProjectionReactor : IReactor<DomainEvent>
{
}

// ❌ 錯誤：未指定泛型
public interface INotifyOrderProjectionReactor : IReactor
{
}
```

理由：

- Message bus / event pipeline 傳遞的是 `DomainEventData`
- 介面層先對齊 transport shape，實作內再轉回 domain event
- 可以避免 reactor interface 與 event bus 型別脫節

### 2. Handler 先接 `DomainEventData`，再轉回 Domain Event

```csharp
public sealed class NotifyOrderProjectionReactor : INotifyOrderProjectionReactor
{
    public Task Handle(DomainEventData eventData)
    {
        var domainEvent = DomainEventMapper.ToDomainEvent(eventData);

        if (domainEvent is OrderPlaced placed)
        {
            // handle
        }

        return Task.CompletedTask;
    }
}
```

禁止把 Reactor 介面直接綁死在單一 domain event class 上。

### 3. Reactor 專注事件驅動協作，不直接承擔 HTTP / Controller concern

Reactor 應只處理：

- event-to-action flow
- projection / archive update
- cross-aggregate coordination
- outbound integration follow-up

Reactor 不應：

- 直接處理 HTTP request / response
- 直接成為 controller action logic
- 把 use case command flow 與 event flow 混在一起

### 4. Reactor 需考慮重送與冪等性

至少要有以下意識：

- at-least-once delivery
- duplicate delivery
- replay / rebuild 情境

對外部 I/O、read-model update 或 notification，應有重複處理保護。

---

## 🎯 推薦責任邊界

```text
Domain Event / Integration Event
  -> Reactor
  -> Archive / Projection / Query Model / Follow-up Application Action
```

Reactor 是 event-driven application collaborator，不是 aggregate 本身的一部分。

---

## ⚠️ 常見錯誤

### 錯誤 1：Reactor 直接宣告 `IReactor<DomainEvent>`

這會讓介面與實際 bus payload 脫節。

### 錯誤 2：Reactor 內直接寫 controller / API concern

Reactor 是 event handler，不是 transport adapter。

### 錯誤 3：Reactor 缺少 idempotency thinking

如果 reactor 會更新 read model、呼叫外部系統、送通知，就不能假設事件只會到一次。

---

## 🔍 檢查清單

- [ ] Reactor 介面使用 `IReactor<DomainEventData>`
- [ ] `Handle(...)` 接收 `DomainEventData`
- [ ] 先轉換為 domain event 再做型別判斷
- [ ] 沒有混入 controller / HTTP concern
- [ ] 有考慮 duplicate delivery / replay 風險

---

## 相關文件

- [usecase-standards.md](usecase-standards.md)
- [archive-standards.md](archive-standards.md)
- [../../operations/runbooks/README.MD](../../operations/runbooks/README.MD)
- [../../ARCHITECTURE.MD](../../ARCHITECTURE.MD)
