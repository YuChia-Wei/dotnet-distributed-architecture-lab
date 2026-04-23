# .NET 編碼規範

本目錄包含所有 .NET 編碼規範文件，每個文件專注於特定領域的標準和最佳實踐。

---

## 📚 規範文件索引

### 核心領域規範
- **[aggregate-standards.md](./aggregate-standards.md)** - Aggregate、Entity、Value Object 和 Domain Event 規範
  - Aggregate Root 設計原則
  - Domain Event 結構與處理
  - Value Object 不可變性設計
  - 軟刪除 (Soft Delete) 實作要求
  - 📋 包含完整程式碼模板

- **[repository-standards.md](./repository-standards.md)** - Repository 模式規範
  - Generic Repository 使用原則
  - EF Core 實作
  - IUnitOfWork 設計
  - 軟刪除過濾機制

- **[usecase-standards.md](./usecase-standards.md)** - Handler/Use Case 層規範
  - Command vs Query 分離原則 (CQRS)
  - WolverineFx Handler 設計
  - Result Pattern 錯誤處理
  - 📋 包含 Command/Query 完整模板

- **[reactor-standards.md](./reactor-standards.md)** - Reactor / 事件處理規範
  - `IReactor<DomainEventData>` 介面規則
  - event-to-action flow 邊界
  - replay / duplicate delivery 注意事項

### 資料存取規範
- **[projection-standards.md](./projection-standards.md)** - Projection/Query Service 模式規範
  - Read Model 設計原則
  - EF Core Query 實作
  - 分頁和複雜查詢處理

- **[archive-standards.md](./archive-standards.md)** - Archive 模式規範
  - Query Model CRUD 操作
  - 跨 Bounded Context 參考資料
  - 事件驅動寫入

- **[mapper-standards.md](./mapper-standards.md)** - Mapper 設計規範
  - Domain 與 Data 物件轉換
  - System.Text.Json 序列化
  - 靜態方法設計原則

### API 與控制層規範
- **[controller-standards.md](./controller-standards.md)** - ASP.NET Core Controller 規範
  - HTTP 狀態碼使用
  - ProblemDetails 錯誤回應
  - 請求驗證
  - Minimal API vs Controller

### 測試規範
- **[test-standards.md](./test-standards.md)** - 測試編碼規範
  - xUnit + BDDfy 測試框架
  - NSubstitute Mocking（禁止 Moq）
  - Contract Tests (DBC Precondition 驗證)
  - WebApplicationFactory 整合測試
  - 📋 包含各種測試模板

- **[profile-configuration-standards.md](./profile-configuration-standards.md)** - Profile / Environment 規範
  - `DOTNET_ENVIRONMENT` / `ASPNETCORE_ENVIRONMENT` 載入規則
  - `appsettings.{Environment}.json` 命名與分工
  - InMemory / Outbox profile-specific DI 約束

---

## 🔴 關鍵原則摘要

### 必須遵守的核心規則

#### 1. Repository 規範
- ❌ 絕對不要創建自定義 Repository 介面
- ✅ 直接使用 `IRepository<Aggregate, AggregateId>`
- ✅ Repository 只能有三個方法: `FindByIdAsync()`, `SaveAsync()`, `DeleteAsync()`

#### 2. Aggregate 設計
- ✅ 每個 Aggregate 必須支援軟刪除 (`IsDeleted`)
- ✅ 使用公開建構子，不用 static factory method
- ✅ Command method 必須有 `Contract.Ensure` 後置條件檢查

#### 3. Handler 設計 (CQRS)
- ✅ Command 和 Query 必須分離
- ✅ 使用 `sealed record` 定義 Command/Query
- ✅ 使用 Constructor Injection，禁止使用 `[FromServices]`
- ✅ Use case / service / mapper / projection 一律由 `IServiceCollection` 顯式註冊，禁止 attribute-based auto registration
- ✅ 返回 `Result<T>` 處理錯誤

#### 4. 測試要求
- ✅ 使用 xUnit + BDDfy 框架
- ✅ 使用 NSubstitute（禁止 Moq）
- ✅ 禁止繼承 BaseTestClass
- ✅ 聚合根 ID 使用 `Guid.NewGuid().ToString()`
- ✅ profile 與 environment 規則見 [profile-configuration-standards.md](./profile-configuration-standards.md)

---

## 📋 快速導航

### 當你要...
- **創建新的 Aggregate** → 查看 [aggregate-standards.md](./aggregate-standards.md)
- **實作 Handler/Use Case** → 查看 [usecase-standards.md](./usecase-standards.md)
- **設計 REST API** → 查看 [controller-standards.md](./controller-standards.md)
- **撰寫測試** → 查看 [test-standards.md](./test-standards.md)
- **處理 profile / environment / DI 分支** → 查看 [profile-configuration-standards.md](./profile-configuration-standards.md)
- **處理查詢** → 查看 [projection-standards.md](./projection-standards.md)
- **管理 Read Model** → 查看 [archive-standards.md](./archive-standards.md)

---

## 🛠️ 技術棧

| 類別 | 技術 | 版本 |
|------|------|------|
| 語言/Runtime | C# / .NET | 8.0 |
| ORM | EF Core | 8.x |
| Message Bus | WolverineFx | Latest |
| 測試框架 | xUnit + BDDfy | Latest |
| Mocking | NSubstitute | Latest |
| Assertion | FluentAssertions | Latest |
| 資料庫 | PostgreSQL | 16.x |
| 訊息佇列 | Kafka | 3.x |

---

## 📚 相關文件

- [架構文件](../../ARCHITECTURE.MD) - 整體架構設計
- [技術棧需求](../../requirement/TECH-STACK-REQUIREMENTS.MD) - 技術棧詳細需求
- [ADR 索引](../../adr/INDEX.md) - 架構決策記錄
- [Code Review 清單](../CODE-REVIEW-CHECKLIST.md) - 程式碼審查清單
