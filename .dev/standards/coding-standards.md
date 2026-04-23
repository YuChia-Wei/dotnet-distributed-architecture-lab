# .NET DDD Wolverine Coding Standards

## 概述

這是 .NET 技術棧的編碼標準主文件，統整所有專門領域的編碼規範。
保留 DDD / Clean Architecture / CQRS / Event Sourcing 的設計精神。

**技術棧**：.NET 10 (C# 14) + WolverineFx + Dapper/EF Core + PostgreSQL

## 專門領域編碼標準

### 1. [Aggregate Standards](./coding-standards/aggregate-standards.md)
- Aggregate Root 設計與事件溯源規範
- Domain Event 生命週期
- Invariant/Contract 的定義方式

### 2. [UseCase Standards](./coding-standards/usecase-standards.md)
- Command / Query 分離
- Handler 與交易邊界
- Input/Output DTO 規範

### 3. [Controller Standards](./coding-standards/controller-standards.md)
- ASP.NET Core API 設計規範
- Request/Response 處理
- 錯誤處理與驗證

### 4. [Repository Standards](./coding-standards/repository-standards.md)
- Repository 介面限制（只允許三個方法）
- Dapper / EF Core 實作規範
- Outbox 與一致性要求

### 5. [Test Standards](./coding-standards/test-standards.md)
- xUnit 測試規範（未來將加入 BDDfy）
- NSubstitute mock 使用規則
- Profile-based testing

### 6. [Projection Standards](./coding-standards/projection-standards.md)
- CQRS Read Model 規範
- EF Core Projection 與效能策略

### 7. [Mapper Standards](./coding-standards/mapper-standards.md)
- DTO / Domain 轉換規則
- Mapper 類別結構

### 8. [Archive Standards](./coding-standards/archive-standards.md)
- Archive Pattern 與軟刪除
- 歷史資料追蹤

### 9. [Reactor Standards](./coding-standards/reactor-standards.md)
- Reactor 介面型別與事件處理邊界
- `DomainEventData` 規則
- replay / duplicate delivery 注意事項

### 10. [Profile / Environment Configuration Standards](./coding-standards/profile-configuration-standards.md)
- `DOTNET_ENVIRONMENT` / `ASPNETCORE_ENVIRONMENT` 規則
- `appsettings.{Environment}.json` 命名與覆蓋邏輯
- InMemory / Outbox profile-specific DI 約束

## 核心設計原則

### 1. Domain-Driven Design (DDD)
- Domain 邏輯集中於 Domain 層
- 使用 Ubiquitous Language
- Bounded Context 明確分離

### 2. Clean Architecture
- 依賴方向由外向內
- Domain 層不依賴框架
- Port & Adapter 模式

### 3. CQRS
- Command 與 Query 分離
- Read Model 與 Write Model 拆分

### 4. Event Sourcing
- 狀態變更以事件為主
- WolverineFx 作為事件/訊息處理框架

### 5. Testing Discipline
- Mutation Testing (Stryker.NET)
- Contract Testing（API/Message 契約）

## 實作規則

### ⚠ 程式碼風格
- **Prefer `this.` usage**：建議使用 `this.` 存取成員
- **資料夾命名**：專案內資料夾使用複數名稱
- **XML 文件註解**：Public API 必須撰寫 XML summary（使用繁體中文，台灣用語）

### ⚠ DTO 命名規則

| 層級 | Input 命名 | Output 命名 |
|------|-----------|------------|
| `<DomainName>.WebApi` | `*Request` | `*Response` |
| `<DomainName>.Applications` | `*Input` | `*Output` / `Result<T>` / `PageResult<T>` |

### ⚠ CQRS & Wolverine 規則

1. **不可變性**：Commands/Queries/Events 應為 immutable（建議使用 `record`）
2. **命名風格**：使用動作優先命名（如 `CreateOrder`、`GetProduct`）
3. **Handler 原則**：保持 Handler 小而專注，避免在 Handler 內處理基礎設施細節（使用注入的服務）
4. **冪等性**：Event 處理必須考慮 at-least-once delivery，在執行外部 I/O 前檢查重複

### ⚠ Command/Query 檔案放置規則

| 類型 | 規則 | 檔案命名 |
|------|------|---------|
| Command | Command + Handler 放同一 `.cs` 檔 | 以 Command 名稱命名 |
| Query | Query + Handler 放同一 `.cs` 檔 | 以 Query 名稱命名 |

### ⚠ Event 放置規則

| Event 類型 | 放置位置 |
|-----------|---------|
| Domain Events | `./src/<Domain>/DomainCore/<DomainName>.Domains/DomainEvents` |
| Domain Event Handlers | `./src/<Domain>/DomainCore/<DomainName>.Applications/DomainEventHandlers` |
| Integration Event Handlers | `./src/<Domain>/Presentation/<DomainName>.Consumer/IntegrationEventHandlers` |
| Integration Event Schema | `./src/BC-Contracts/Lab.MessageSchemas.<Domain>` |

### ⚠ Repository 設計規範（嚴格 CQRS）

Repository 是取得 Aggregate 進行**修改**的唯一入口，遵循 by-identity 原則。

#### Generic Repository 介面

```csharp
public interface IDomainRepository<TAggregateRoot, TId>
{
    // 基本操作
    Task<TAggregateRoot?> FindByIdAsync(TId id);
    Task SaveAsync(TAggregateRoot aggregate);
    Task DeleteAsync(TAggregateRoot aggregate);

    // 批次操作（效能優化，語意相同）
    Task<IReadOnlyList<TAggregateRoot>> FindByIdsAsync(IEnumerable<TId> ids);
    Task SaveAllAsync(IEnumerable<TAggregateRoot> aggregates);
}
```

#### Repository 規則

| 規則 | 說明 |
|------|------|
| ✅ 允許 | `FindByIdAsync(TId)` - by identity 取得單一 Aggregate |
| ✅ 允許 | `FindByIdsAsync(List<TId>)` - 批次版本，效能優化 |
| ❌ 禁止 | 回傳 DTO（那是 QueryService 職責） |
| ❌ 禁止 | 複雜查詢如 `GetByCustomerId()`（應使用 QueryService 先取得 IDs） |
| ❌ 禁止 | 自定義 Repository 介面擴展查詢方法 |

#### Query Side 分層（嚴格 CQRS）

Query Side 採用 **Query Repository + Query Service** 雙層設計，分離資料存取與業務邏輯。

> 📖 模式理由詳見 [query-side-layering-rationale.MD](./rationale/query-side-layering-rationale.MD)

#### 介面與實作放置位置

| 類型 | 介面位置 | 實作位置 |
|------|---------|---------|
| `IDomainRepository<T, TId>` | `BuildingBlocks.Application` | `<Domain>.Infrastructure/Repositories` |
| `I<Domain>QueryRepository` | `<Domain>.Applications/Ports` | `<Domain>.Infrastructure/QueryRepositories` |
| `I<Domain>QueryService` | `<Domain>.Applications/Ports` | `<Domain>.Applications/QueryServices` |

**目錄結構範例**：
```
<DomainName>.Applications/
├── Ports/                       # 介面定義 (Ports)
│   ├── IOrderQueryRepository.cs
│   └── IOrderQueryService.cs
├── QueryServices/               # Query Service 實作
│   └── OrderQueryService.cs
├── Commands/
└── Queries/

<DomainName>.Infrastructure/
├── Repositories/                # Domain Repository 實作
│   └── OrderDomainRepository.cs
└── QueryRepositories/           # Query Repository 實作
    └── OrderQueryRepository.cs
```

> 💡 **為什麼 QueryService 介面和實作都在 Application？**
> QueryService 是查詢業務邏輯，不是技術基礎設施。它組合其他 Ports（QueryRepository），不直接操作資料庫，符合 Clean Architecture。

| 層級 | 類別 | 職責 | 位置 |
|------|------|------|------|
| Infrastructure | Query Repository | 純資料存取，回傳 DTO/ID | `<Domain>.Infrastructure/QueryRepositories` |
| Application | Query Service | 查詢業務邏輯、組合、計算 | `<Domain>.Applications/QueryServices` |

#### Query Repository 規範

```csharp
// Infrastructure 層 - 純資料存取
public interface IOrderQueryRepository
{
    Task<OrderDto?> GetByIdAsync(Guid orderId);
    Task<IReadOnlyList<OrderDto>> GetByCustomerIdAsync(Guid customerId);
    Task<IReadOnlyList<Guid>> GetIdsByStatusAsync(OrderStatus status);
}
```

| 規則 | 說明 |
|------|------|
| ✅ 允許 | 回傳 DTO、ID 列表 |
| ✅ 允許 | 使用 Dapper 或 EF Core Projection |
| ❌ 禁止 | 包含業務邏輯 |
| ❌ 禁止 | 回傳 Aggregate |

#### Query Service 規範

```csharp
// Application 層 - 查詢業務邏輯
public interface IOrderQueryService
{
    // 組合多個 Repository 查詢
    Task<OrderWithItemsDto> GetOrderWithItemsAsync(Guid orderId);

    // 包含計算/轉換邏輯
    Task<OrderSummaryDto> GetOrderSummaryAsync(Guid customerId);

    // 提供 IDs 給 Command Handler 使用
    Task<IReadOnlyList<Guid>> GetPendingOrderIdsForCustomerAsync(Guid customerId);
}
```

| 規則 | 說明 |
|------|------|
| ✅ 允許 | 組合多個 Query Repository |
| ✅ 允許 | 包含計算、轉換邏輯 |
| ✅ 允許 | 回傳 ID 列表供 Command 使用 |
| ❌ 禁止 | 直接存取資料庫 |
| ❌ 禁止 | 回傳 Aggregate |

#### 嚴格 CQRS 使用範例

```csharp
// 情境：更新特定客戶所有待處理訂單
public async Task HandleAsync(UpdatePendingOrdersCommand cmd)
{
    // Step 1: Query Service 取得符合條件的 Order IDs
    var orderIds = await _queryService.GetPendingOrderIdsForCustomerAsync(cmd.CustomerId);

    // Step 2: Domain Repository 載入 Aggregates 並修改
    var orders = await _repository.FindByIdsAsync(orderIds);
    foreach (var order in orders)
    {
        order.UpdateSomething();
    }
    await _repository.SaveAllAsync(orders);
}
```

> ⚠️ **注意**：批次更新多個 Aggregate 時，請考慮是否違反「一個交易只修改一個 Aggregate」原則。如不需強一致性，建議透過 Message Bus 發送多個獨立 Command。

### ⚠ ORM 使用策略

| 場景 | 選擇 | 理由 |
|------|------|------|
| Command (Write) | Dapper + Npgsql | 精確控制 SQL、效能最佳化 |
| Query (Read/Projection) | EF Core 或 Dapper | 快速開發或效能需求 |
| Complex Query | Dapper | 複雜 SQL、效能關鍵查詢 |

### ⚠ Profile-Based Testing
- **禁止使用 BaseTestClass / BaseUseCaseTest 作為測試父類**
- 所有測試必須支援 `test-inmemory` 與 `test-outbox` profiles
- 使用 `appsettings.*.json` 控制 profile
- profile 命名、載入、DI 分支與 profile-specific infra 規則以 [Profile / Environment Configuration Standards](./coding-standards/profile-configuration-standards.md) 為準

### ⚠ Outbox / Inbox Pattern
- 使用 WolverineFx 的 Outbox 機制確保事件發佈的可靠性
- 如導入 Inbox Pattern，Consumer 端亦應遵循相同慣例
- 交易邊界：命令處理內的狀態改變需與儲存一致性策略對齊

## 自動化檢查

```bash
# 執行 dotnet 版完整檢查
.ai/scripts/check-all.sh

# Spec compliance
.ai/scripts/check-spec-compliance.sh <spec-file> <task-name>

# Mutation testing
.ai/scripts/check-mutation-coverage.sh
```

## 相關文件

- [最佳實踐](./best-practices.md)
- [反模式](./anti-patterns.md)
- [編碼指南](./coding-guide.md)
- [程式碼審查清單](./CODE-REVIEW-CHECKLIST.md)
