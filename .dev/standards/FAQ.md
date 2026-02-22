# .NET CA + WolverineFx 常見問題 (FAQ)

## 架構設計問題

### 為什麼要使用 Event Sourcing？
- 完整審計軌跡
- 可回放狀態
- 支援 CQRS
- 易於實作撤銷/重做

### Command 和 Query 的區別是什麼？
- **Command**: 改變狀態，回傳 `CqrsOutput`
- **Query**: 讀取資料，回傳 DTO

```csharp
// Command 範例
public sealed record CreatePlanCommand(string Name);

// Query 範例
public sealed record GetPlanQuery(string PlanId);
```

### 什麼時候使用 Reactor/Handler？
當跨 Aggregate 的副作用需要處理時使用（通知、同步、快取等）。

### 為什麼 UseCase Input/Output 要保持簡單？
Input/Output 是資料傳輸物件，應避免包含業務邏輯，保持序列化友好。

## 開發實作問題

### 為什麼 Repository 只有三個方法？
為了強制 CQRS 分離與保持 Domain 純粹性。查詢應該透過 Projection/Inquiry。

### 為什麼 Domain Event 必須對應 spec？
避免過度設計與規格偏離，確保事件模型與需求一致。

### 為什麼不能直接使用 DateTime.UtcNow？
不可測試且不一致，必須使用 DateProvider/TimeProvider 以利測試控制。
