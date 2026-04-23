# Generic Repository Only Rationale

## Decision Pattern

command side 預設只使用 generic repository：

- `IDomainRepository<TAggregate, TId>`

不建立沒有新增語意的 custom repository interface。

## Why

### 1. 避免空殼抽象

像 `IProductRepository : IRepository<Product, ProductId>` 這類介面若沒有新增能力，只是多一個名字，不會增加邊界清晰度。

### 2. 避免 Repository 職責膨脹

一旦為每個 aggregate 建專屬 repository interface，團隊很容易把查詢方法也塞進去，破壞 CQRS 邊界。

### 3. Command side 的需求其實很穩定

對 aggregate 的 command-side persistence，核心需求通常只有：

- load by identity
- save
- delete

這些不值得為每個 aggregate 重複宣告一次。

## Why Not

### 每個 Aggregate 一個專屬 Repository Interface

只有在它承載額外穩定語意、而且確實不是 query concern 時，才可能有理由存在。  
否則大多只是樣板與重複命名。

## Practical Rule

- command side / use case write side: generic repository
- query side: query repository / query service
- 不要把 DTO 查詢方法加進 domain repository

## Relationship to Use Case Rule

- `Use Case` 是 HTTP 與 application inbound port 的主入口
- `IDomainRepository<TAggregate, TId>` 是 use case / application service / message handler 在 write side 的預設 persistence port
- repository 規則不改變 `Use Case`、`Command`、`Handler` 的責任邊界，只限制 write-side persistence vocabulary

## References

- Microsoft, CQRS pattern:
  - [https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs](https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs)
- Martin Fowler, CQRS:
  - [https://martinfowler.com/bliki/CQRS.html](https://martinfowler.com/bliki/CQRS.html)
