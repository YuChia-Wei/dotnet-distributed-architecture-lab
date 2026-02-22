# ADR-002 - EF Core Configuration Location (.NET)

## Date
2025-08-01

## Status
Accepted

## Context
EF Core 設定（DbContext、連線字串、Migration 設定）曾被放在 Web/Api 層附近，造成層級混淆：
- ORM 屬於 Persistence concern，不是 Web concern
- 其他配置都位於 `Infrastructure` 區域
- Web 層應只保留 API 與 middleware

## Decision
將 EF Core 設定移到 `Infrastructure/Persistence`（或 `Infrastructure/Configuration/Persistence`），保持與 DI/Options 註冊集中。

## Consequences

### Positive
- **層級清楚**：ORM 明確歸屬 persistence
- **結構一致**：所有配置集中在 Infrastructure
- **可維護性提升**

### Negative
- **需要調整 using/命名空間**

## Alternatives Considered

### Option 1: 保留在 Web/Api 區域
- **Pros**：不用搬移
- **Cons**：層級錯誤、容易誤導

### Option 2: 放在 Infrastructure 根目錄
- **Pros**：更扁平
- **Cons**：不同類型配置混在一起

### Option 3: 獨立 Persistence 專案
- **Pros**：層級最清楚
- **Cons**：目前規模不需要，增加專案數量

## Related Decisions
- [ADR-003](./ADR-003-spring-config-structure.md)
