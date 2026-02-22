# ADR-001 - Use Case Namespace Structure (.NET)

## Date
2025-08-01

## Status
Accepted

## Context
專案採用 Clean Architecture + CQRS，因此 Use Case 分為：
- Commands：修改狀態
- Queries：讀取資料
- Reactors：跨 Aggregate 的事件處理

需要決定 `Application/UseCases/Ports/In` 是否再細分為 `Command/Query/Reactor` 子命名空間。

## Decision
維持 **扁平結構**：Command/Query 共用 `UseCases.Ports.In`；Reactor 使用 `UseCases.Ports.In.Reactor`。

## Consequences

### Positive
- **簡潔**：扁平結構易於瀏覽
- **一致**：符合常見 DDD/CA 專案慣例
- **命名清楚**：Use Case 名稱已表達用途
- **彈性**：不需深層目錄即可定位用例
- **IDE 友善**：可透過介面繼承過濾

### Negative
- **無顯式區隔**：Command/Query 同一命名空間
- **未來增長風險**：用例數量過大時可能雜亂

### Neutral
- 開發者需依命名與介面繼承辨識用例型別

## Alternatives Considered

### Option 1: 拆成 Command/Query/Reactor 命名空間
- **Description**：`UseCases.Ports.In.Command` / `UseCases.Ports.In.Query` / `UseCases.Ports.In.Reactor`
- **Pros**：CQRS 關注點清楚
- **Cons**：階層加深、導航成本增加
- **Reason for rejection**：目前規模不需要

### Option 2: 以 Aggregate + 類型分層
- **Description**：`Plan.UseCases.Ports.In.Command` 等
- **Pros**：最顯式
- **Cons**：過深、過度設計

## Notes
- Reactor 仍保留子命名空間，因為跨 Aggregate 關注點特殊
- 若單一 Aggregate 用例超過 50，再考慮拆分
