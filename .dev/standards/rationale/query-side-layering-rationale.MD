# Query Side Layering Rationale

## Decision Pattern

query side 採雙層：

- Query Repository
- Query Service

## Why

### 1. 分離資料存取與查詢業務邏輯

Query Repository 應只處理資料取得。  
Query Service 則處理：

- 組合多個查詢來源
- 過濾與轉換
- 查詢層的業務計算

### 2. 維持 Clean Architecture 邊界

若 Query Service 直接到處碰資料庫，application 層就會混入太多技術細節。  
若把查詢方法塞進 domain repository，又會模糊 command/query 邊界。

### 3. 保持 Query 與 Aggregate 解耦

read model 不一定需要 aggregate。  
query side 回 DTO / projection / ids，通常更直接、更便宜，也更安全。

## Why Not

### 只有 Query Service，沒有 Query Repository

缺點：

- 資料存取與查詢邏輯糾纏
- 較難替換資料來源
- 較難測試 service 的純查詢邏輯

### 在 Domain Repository 內擴充查詢方法

缺點：

- command/query 邊界被打穿
- repository 可能被濫用成全能資料存取物件

## Practical Rule

- Query Repository: infrastructure / pure data access
- Query Service: application / query orchestration
- Domain Repository: 只服務 aggregate write-side lifecycle

## Relationship to Use Case Rule

- Query-side HTTP entry can be modeled as an explicit `Use Case`
- Whether query entry is named `Use Case` or `Query`, the read-side implementation should still prefer `Query Repository` + `Query Service`
- Query-side vocabulary must not drag reads back into aggregate persistence APIs

## References

- Microsoft, CQRS pattern:
  - [https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs](https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs)
- Martin Fowler, CQRS:
  - [https://martinfowler.com/bliki/CQRS.html](https://martinfowler.com/bliki/CQRS.html)
