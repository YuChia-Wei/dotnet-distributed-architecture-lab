# ADR-018 - PBI State Transition Invariant Handling (.NET)

## Date
2025-08-18

## Status
Accepted

## Context
在 Event Sourcing 架構下，PBI (Product Backlog Item) 的 Task 狀態變更會觸發 PBI 狀態轉換，例如：
- 所有 tasks 都 DONE → PBI 變成 DONE
- DONE 中有 task 回退 → PBI 回到 IN_PROGRESS
- 刪除 task 後若剩餘 tasks 全 DONE → PBI 變成 DONE
- DONE 狀態新增 task → PBI 回到 IN_PROGRESS

事件序列：
1. `TaskCreated`
2. `TaskMoved`
3. `TaskDeleted`
4. `PbiCompleted`
5. `PbiWorkRegressed`

這些事件之間會出現**臨時不一致狀態**，例如 PBI 已是 DONE 但 tasks 尚未全部 DONE。此時若強制 invariant，會阻斷必要流程。

（Frontend 仍存在 RTK Query 相關處理，保留為跨職能參考。）

## Decision
1. **後端**：允許事件處理過程的臨時不一致，並在 invariant 檢查中排除該狀態：
```csharp
// 當 PBI 是 DONE 但不是所有 tasks 都 DONE 時
if (state == PbiState.Done && !AllTasksDone())
{
    // 臨時狀態 - Task 已移動但 PBI 狀態尚未更新
    // PbiWorkRegressed 事件會修正這個狀態
    // 所以不強制執行 invariant
}
```

2. **前端（參考）**：調整 RTK Query 的 cache 更新策略，避免 optimistic update 成功後立即 invalidate。

## Consequences

### Positive
- 允許正常的 PBI 狀態回退流程
- 保持事件順序與最終一致性
- 不影響其他 invariant

### Negative
- Invariant 檢查邏輯更複雜
- 需要理解事件處理時序

## Alternatives Considered

### Option 1: 嚴格執行 Invariant
- **Pros**：邏輯簡單
- **Cons**：阻斷必要流程

### Option 2: 延遲 Invariant 檢查
- **Pros**：避免臨時狀態
- **Cons**：需大改事件處理機制

### Option 3: 合併事件
- **Pros**：沒有臨時狀態
- **Cons**：破壞事件語義

## Notes
### Implementation Details
1. Invariant 檢查需識別臨時不一致模式
2. 事件產生順序必須固定
3. PBI 狀態轉換規則：
   - Task → DONE，若全 DONE → PBI DONE
   - Task 從 DONE 回退 → PBI IN_PROGRESS
   - 刪除 task 後若全 DONE → PBI DONE
   - DONE 狀態新增 task → PBI IN_PROGRESS
4. 測試覆蓋：
   - 事件順序的單元測試
   - 最終狀態的整合測試

## References
- Event Sourcing Pattern
- DDD Aggregate Invariants
- 相關程式碼：`ProductBacklogItem.cs`（`MoveTask` / `EnsureInvariant`）

