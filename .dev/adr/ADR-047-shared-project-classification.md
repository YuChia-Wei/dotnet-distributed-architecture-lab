# ADR-047: 共用專案分類與依賴規則（Shared Project Classification & Dependency Rules）

## 狀態

Accepted (2026-02-17)

## 背景

本專案採用多 Bounded Context (BC) 架構，擁有三個跨領域共用區域：

- `src/BuildingBlocks/` — 架構基礎設施
- `src/Shared/` — 通用領域核心
- `src/BC-Contracts/` — 跨 BC 溝通合約

隨著專案演進，需要正式定義各共用專案的職責邊界、命名規則與依賴方向約束，避免職責混淆並確保新進開發人員能快速理解分類原則。

### DDD 中 Shared Kernel 的定義

在 Eric Evans 的 DDD 中，**Shared Kernel** 是一個特定的 Context Mapping 模式：

> 兩個或多個 Bounded Context **共同擁有並維護**的一小部分 Domain Model。變更需要雙方協調同意。

Shared Kernel 的核心特徵是：**它包含業務語義（Domain concepts），且被多個 BC 共享**。

這與 **Published Language**（跨 BC 通訊用的公開合約，不深入內部模型）是不同的概念。本專案中：

- `SharedKernel` 對應 DDD 的 **Shared Kernel** — 共享的領域概念
- `BC-Contracts` 對應 DDD 的 **Published Language** — BC 對外發布的通訊合約

兩者雖都是「跨 BC 共用」，但在 DDD 語義上有根本差異：

| 面向 | Shared Kernel | Published Language (BC-Contracts) |
|------|---------------|-----------------------------------|
| 使用位置 | BC 的 **Domain 層內部** | BC 的 **Application/Infrastructure 邊界** |
| 目的 | 避免重複定義通用領域概念 | 定義 BC 間的溝通協議 |
| 變更影響 | 所有引用的 BC 都受影響 | 只影響通訊雙方的整合層 |
| 典型內容 | Value Objects、Enums | Integration Events、Request/Reply Contracts |

## 決策

### 三層分類

| 專案 | DDD 概念 | 職責 | Namespace |
|------|---------|------|-----------|
| **BuildingBlocks** | 架構基礎設施 | 無業務語義的抽象基底與介面 | `Lab.BuildingBlocks.<Layer>` |
| **SharedKernel** | Shared Kernel | 跨 BC 共享的通用領域概念 | `Lab.SharedKernel` |
| **BC-Contracts** | Published Language | BC 間通訊合約 | `Lab.BoundedContextContracts.<Domain>` |

### 各專案詳細定義

#### BuildingBlocks（架構基礎設施）

- **用途**：提供 DDD / Clean Architecture 架構的基底類別與介面
- **特性**：技術導向、無業務語義、可跨任何專案重用
- **依賴權限**：所有層均可引用
- **範例**：`AggregateRoot<TId>`, `ValueObject`, `IIntegrationEvent`, `IDomainRepository<T, TId>`, `IIntegrationEventPublisher`

#### SharedKernel（通用領域核心）

- **用途**：存放被多個 BC 在 Domain 層內部直接使用的通用領域概念
- **特性**：業務導向、包含領域語義、變更影響所有引用的 BC
- **依賴權限**：**Domain 層可引用**（因為它本身就是 Domain 概念的共享）
- **範例**：`Money(decimal Amount, string Currency)`, `EmailAddress`, `DateRange`, 通用業務 Enums

#### BC-Contracts（跨 BC 溝通合約）

- **用途**：定義 Bounded Context 之間的 Published Language
- **特性**：業務導向、僅用於 BC 邊界上的通訊、包含領域關聯的合約型別
- **依賴權限**：**Domain 層禁止引用**，僅 Application / Infrastructure / Presentation 層可引用
- **內部子分類**：
  - `IntegrationEvents/` — 非同步事件合約（MQ Payload）
  - `Interactions/` — Request/Reply 合約（同步或 RPC）
  - `DataTransferObjects/` — 跨 BC 查詢回傳合約

### 依賴方向約束

```
BuildingBlocks ← (所有層均可引用)
SharedKernel   ← Domain / Application / Infrastructure / Presentation
BC-Contracts   ← Application / Infrastructure / Presentation（Domain 禁止引用）
```

**關鍵原則**：

- `SharedKernel` 的型別會出現在 BC 的 **Domain 層** `using` 中
- `BC-Contracts` 的型別**只會**出現在 **Application/Infrastructure/Presentation 層** 的 `using` 中
- `BC-Contracts` 專案可以依賴 `BuildingBlocks`（如引用 `IIntegrationEvent` 介面），但 `BuildingBlocks` 不可依賴 `BC-Contracts`
- `SharedKernel` 可以依賴 `BuildingBlocks`，但不可依賴 `BC-Contracts`

### 分類決策樹

判斷新型別應放在哪個共用專案：

```
問題 1：這個型別是否與業務邏輯相關？
├─ 否（純架構抽象，如 base class、技術介面）
│   → BuildingBlocks
│
└─ 是（包含業務語義）
    │
    問題 2：這個型別是否被 BC 的 Domain Model 在內部直接使用？
    ├─ 是，且多個 BC 都在 Domain 層內部使用
    │   → SharedKernel
    │
    └─ 否，它只出現在 BC 之間的訊息/通訊邊界上
        → BC-Contracts
```

### 具體分類範例

| 型別 | 分類 | 原因 |
|------|------|------|
| `AggregateRoot<TId>` | **BuildingBlocks** | 純架構抽象，無業務含義 |
| `ValueObject` | **BuildingBlocks** | Domain 基底類別，技術層面的相等性比較機制 |
| `IIntegrationEvent` | **BuildingBlocks** | 定義整合事件的技術介面，無業務語義 |
| `IDomainRepository<T, TId>` | **BuildingBlocks** | Repository 模式的技術介面 |
| `Money(decimal Amount, string Currency)` | **SharedKernel** | 多個 BC 的 Domain Model 都需要在內部使用金錢概念 |
| `EmailAddress` | **SharedKernel** | 通用 Value Object，多個 BC 可能在 Domain 內使用 |
| `DateRange` | **SharedKernel** | 多個 BC 可能使用的時間範圍值物件 |
| `OrderPlaced { OrderId, Quantity }` | **BC-Contracts** | 只在 Order BC 發出、其他 BC 接收的跨邊界溝通事件 |
| `ReserveInventoryRequestContract` | **BC-Contracts** | Inventory BC 對外公佈的 Request/Reply 互動合約 |
| `OrderDetailsResponse` | **BC-Contracts** | 跨 BC 查詢時的回傳合約 |

## 考量的替代方案

### 方案 A：合併 SharedKernel 與 BC-Contracts

將所有跨 BC 共用內容放在單一專案中。

**優點**：
- 管理較簡單，只需維護一個共用專案

**缺點**：
- 違反 DDD 的 Shared Kernel 與 Published Language 分離原則
- Domain 層被迫可見 Integration Events 等不該接觸的通訊合約
- 破壞 Clean Architecture 的依賴方向

### 方案 B：BC-Contracts 放入各 Domain 資料夾

每個 BC 的合約放在該 BC 的資料夾下。

**優點**：
- 合約與發布者在同一位置

**缺點**：
- 消費者需要引用發布者的專案，增加耦合
- 跨 BC 合約的獨立版本管理變困難
- 不符合 Published Language 獨立於任一 BC 的本質

## 後果

### 正面

- ✅ DDD 語義清晰：三個專案分別對應架構基礎設施、Shared Kernel、Published Language
- ✅ 依賴方向可驗證：透過 Domain 層是否引用 BC-Contracts 即可判斷違規
- ✅ 變更影響範圍可控：各專案職責明確，變更時影響範圍可預測
- ✅ 未來可獨立打包：BC-Contracts 可獨立抽成 NuGet 供其他 BC 引用

### 負面

- ⚠️ 需維護三個共用專案的邊界紀律
- ⚠️ 新型別放置需要判斷，有一定學習成本（可參照決策樹）
- ⚠️ SharedKernel 變更需協調所有引用的 BC

## 相關

- [project-structure.md](../standards/project-structure.md) — 專案結構指南
- [bc-contracts.md](../../docs/program-design/bc-contracts.md) — BC-Contracts 早期設計筆記
