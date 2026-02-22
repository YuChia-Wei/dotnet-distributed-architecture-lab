# ADR-003 - .NET Configuration Structure (DI & Options)

## Date
2025-08-01

## Status
Accepted

## Context
曾提議建立 `Infrastructure/DI` 來集中 `IServiceCollection` 註冊。但目前的組態檔案數量與複雜度不高，且現有做法以「功能關注點」分組更容易維護。

## Decision
維持 **扁平的配置結構**，以功能分組的 `*Config` / `*Module` 檔案為主，不另外建立 `di` 子目錄。

## Consequences

### Positive
- **符合 ASP.NET Core 慣例**：使用 `IServiceCollection` 擴充方法
- **功能導向**：以業務/技術關注點分組（Persistence、Messaging、UseCases）
- **清楚命名**：`*Config` / `*Module` 已表達 DI 目的
- **避免過度設計**

### Negative
- **無單一 DI 目錄**：註冊分散於多個檔案
- **規模擴張時需再評估**

## Alternatives Considered

### Option 1: `Infrastructure/DI` 目錄集中所有註冊
- **Pros**：DI 集中
- **Cons**：違反以功能分組的原則

### Option 2: 依技術層分組（Web / Data / Domain）
- **Pros**：技術層清楚
- **Cons**：目前規模不需要，容易產生空目錄

## Related Decisions
- [ADR-002](./ADR-002-orm-config-location.md)

## Notes
- 若超過 10 個組態檔可再考慮 `Infrastructure/Configuration/{Persistence|Messaging|UseCases}` 分層
- **不以 DI 技術為分組依據**（避免 `config.di`）
