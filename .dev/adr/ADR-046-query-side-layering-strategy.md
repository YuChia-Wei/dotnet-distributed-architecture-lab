# ADR-046: Query Side 分層策略（Query Repository + Query Service）

## 狀態

已接受 (Accepted)

## 日期

2026-02-08

## 背景

在實作 CQRS 架構時，Query Side 的設計有多種做法：

1. **簡化版**：QueryService 同時處理資料存取與業務邏輯
2. **分層版**：Query Repository（資料存取）+ Query Service（業務邏輯）

團隊需要決定採用哪種方式，以確保：
- 程式碼職責明確
- 可測試性高
- 符合 Clean Architecture 原則

## 決策

採用 **Query Repository + Query Service 雙層設計**：

| 層級 | 類別 | 職責 | 位置 |
|------|------|------|------|
| Infrastructure | Query Repository | 純資料存取 | `<Domain>.Infrastructure/QueryRepositories` |
| Application | Query Service | 查詢業務邏輯 | `<Domain>.Applications/QueryServices` |

### Query Repository

- 位於 Infrastructure 層
- 純資料存取，無業務邏輯
- 回傳 DTO 或 ID 列表
- 可使用 Dapper 或 EF Core Projection

### Query Service

- 位於 Application 層
- 組合多個 Query Repository
- 包含計算、轉換、過濾等業務邏輯
- 可回傳 ID 列表供 Command Handler 使用

## 與 Domain Repository 的區別

| 面向 | Domain Repository | Query Repository |
|------|------------------|------------------|
| 職責 | 取得 Aggregate 進行修改 | 取得 DTO 進行展示 |
| 回傳類型 | Aggregate | DTO / ID |
| 使用場景 | Command Handler | Query Handler / Query Service |
| 位置 | Infrastructure | Infrastructure |

## 考量的替代方案

### 方案 A：簡化版 QueryService

QueryService 直接存取資料庫，不分出 Query Repository。

**優點**：
- 層級少，開發較快

**缺點**：
- 違反單一職責
- 難以測試業務邏輯
- 換底層框架時需大改

### 方案 B：Domain Repository 擴展查詢方法

在 Domain Repository 加入複雜查詢方法。

**優點**：
- 簡單

**缺點**：
- 模糊 Command/Query 邊界
- Repository 可能回傳 Aggregate 給 Query 使用（不安全）

## 後果

### 正面

- ✅ 職責明確：資料存取與業務邏輯分離
- ✅ 可測試性高：Query Service 可 mock Query Repository
- ✅ 符合 Clean Architecture Port/Adapter
- ✅ Query Service 釋出來做查詢業務服務

### 負面

- ⚠️ 層級較多，需撰寫更多介面
- ⚠️ 簡單查詢可能顯得過度設計

## 相關

- [ADR-029: No Custom Repository Interfaces](./ADR-029-no-custom-repository-interfaces.md)
- [Coding Standards: Repository 設計規範](../standards/coding-standards.md)
