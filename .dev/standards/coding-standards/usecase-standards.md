# UseCase 編碼規範 (.NET)

本文件定義 Use Case / Handler 層的編碼標準，包含 Command、Query、Input/Output 和 Handler 設計。

---

## 📌 概述

UseCase/Handler 必須遵守 CQRS 分離與交易邊界規範。

- **Command** 修改狀態，返回 `Result<T>`
- **Query** 只讀取，返回 DTO
- **Handler** 負責協調 Domain 和 Infrastructure

---

## 🏷️ Pattern 標記（自動化檢查用）

以下標記供自動化 Code Review 腳本使用：

```yaml
# Handler 規則
Pattern (required): Handle\(
Pattern (required): private readonly

# 禁止規則
Pattern (forbidden, i, ignore-comment): IServiceProvider|ServiceLocator
Pattern (forbidden): new .*Repository\(
```

---

## 🔴 必須遵守的規則 (MUST FOLLOW)

### 1. Command 與 Query 必須分離 (CQRS)

WolverineFx handlers 不可混用讀寫責任。

```csharp
// ✅ 正確：Command 分離
public sealed record CreateProductCommand(
    string ProductId,
    string Name,
    string UserId) : ICommand<Result<ProductId>>;

public sealed class CreateProductHandler
{
    private readonly IRepository<Product, ProductId> _repository;
    
    public CreateProductHandler(IRepository<Product, ProductId> repository)
    {
        _repository = repository;
    }
    
    public async Task<Result<ProductId>> Handle(
        CreateProductCommand command,
        CancellationToken ct)
    {
        var product = new Product(
            ProductId.From(command.ProductId),
            command.Name,
            command.UserId
        );
        
        await _repository.SaveAsync(product, ct);
        
        return Result.Success(product.Id);
    }
}

// ✅ 正確：Query 分離
public sealed record GetProductQuery(string ProductId) : IQuery<ProductDto?>;

public sealed class GetProductHandler
{
    private readonly IProductQueryService _queryService;
    
    public GetProductHandler(IProductQueryService queryService)
    {
        _queryService = queryService;
    }
    
    public async Task<ProductDto?> Handle(GetProductQuery query, CancellationToken ct)
    {
        return await _queryService.GetByIdAsync(ProductId.From(query.ProductId), ct);
    }
}
```

---

### 2. 依賴注入必須透過 Constructor

禁止使用 `IServiceProvider` 或 Service Locator 模式。

```csharp
// ✅ 正確：Constructor Injection
public sealed class CreateProductHandler
{
    private readonly IRepository<Product, ProductId> _repository;
    private readonly IUnitOfWork _unitOfWork;
    private readonly ILogger<CreateProductHandler> _logger;
    
    public CreateProductHandler(
        IRepository<Product, ProductId> repository,
        IUnitOfWork unitOfWork,
        ILogger<CreateProductHandler> logger)
    {
        _repository = repository;
        _unitOfWork = unitOfWork;
        _logger = logger;
    }
}

// ❌ 錯誤：Service Locator
public sealed class CreateProductHandler
{
    public CreateProductHandler(IServiceProvider provider)
    {
        var repo = provider.GetService<IRepository<Product, ProductId>>();  // FORBIDDEN!
    }
}
```

---

### 3. 必須定義明確的 Command/Query Records

使用 `record` 定義 Input，WolverineFx 會自動處理。

```csharp
// ✅ 正確：使用 record 定義 Command
public sealed record CreateProductCommand(
    string ProductId,
    string Name,
    string UserId,
    string? Description = null) : ICommand<Result<ProductId>>;

// ✅ 正確：使用 record 定義 Query
public sealed record GetProductsQuery(
    string? Filter = null,
    int Page = 0,
    int Size = 20) : IQuery<PagedResult<ProductDto>>;
```

---

### 4. Handler 必須返回 Result Pattern

Command Handler 使用 `Result<T>` 包裝返回值，處理成功與失敗情況。

```csharp
// ✅ 正確：返回 Result<T>
public async Task<Result<ProductId>> Handle(
    CreateProductCommand command,
    CancellationToken ct)
{
    try
    {
        var product = new Product(...);
        await _repository.SaveAsync(product, ct);
        await _unitOfWork.CommitAsync(ct);
        
        return Result.Success(product.Id);
    }
    catch (DomainException ex)
    {
        _logger.LogWarning(ex, "Domain validation failed");
        return Result.Failure<ProductId>(ex.Message);
    }
}
```

---

## 🔍 檢查清單

### Handler
- [ ] 使用 Constructor Injection
- [ ] 沒有使用 `IServiceProvider`
- [ ] Command Handler 返回 `Result<T>`

### CQRS 分離
- [ ] Command 和 Query 是獨立的 Handler
- [ ] Command 使用 Repository
- [ ] Query 使用專門的 QueryService

### Command/Query Records
- [ ] 使用 `sealed record`
- [ ] 實作 `ICommand<T>` 或 `IQuery<T>`
- [ ] 使用簡單類型 (string, int, etc.)
- [ ] 可選參數有預設值

---

## 📋 快速複製模板

### Command + Handler 模板

```csharp
// Command
public sealed record Create[Aggregate]Command(
    string [Aggregate]Id,
    string Name,
    string UserId) : ICommand<Result<[Aggregate]Id>>;

// Handler
public sealed class Create[Aggregate]Handler
{
    private readonly IRepository<[Aggregate], [Aggregate]Id> _repository;
    private readonly IUnitOfWork _unitOfWork;
    private readonly ILogger<Create[Aggregate]Handler> _logger;

    public Create[Aggregate]Handler(
        IRepository<[Aggregate], [Aggregate]Id> repository,
        IUnitOfWork unitOfWork,
        ILogger<Create[Aggregate]Handler> logger)
    {
        _repository = repository;
        _unitOfWork = unitOfWork;
        _logger = logger;
    }

    public async Task<Result<[Aggregate]Id>> Handle(
        Create[Aggregate]Command command,
        CancellationToken ct)
    {
        try
        {
            var aggregate = new [Aggregate](
                [Aggregate]Id.From(command.[Aggregate]Id),
                command.Name,
                command.UserId
            );

            await _repository.SaveAsync(aggregate, ct);
            await _unitOfWork.CommitAsync(ct);

            return Result.Success(aggregate.Id);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to create [Aggregate]");
            return Result.Failure<[Aggregate]Id>(ex.Message);
        }
    }
}
```

### Query + Handler 模板

```csharp
// Query
public sealed record Get[Aggregate]Query(string [Aggregate]Id) : IQuery<[Aggregate]Dto?>;

// Handler
public sealed class Get[Aggregate]Handler
{
    private readonly I[Aggregate]QueryService _queryService;

    public Get[Aggregate]Handler(I[Aggregate]QueryService queryService)
    {
        _queryService = queryService;
    }

    public async Task<[Aggregate]Dto?> Handle(
        Get[Aggregate]Query query,
        CancellationToken ct)
    {
        return await _queryService.GetByIdAsync(
            [Aggregate]Id.From(query.[Aggregate]Id), ct);
    }
}
```

---

## 📂 程式碼範例

更多完整範例請參考：

| 範例 | 路徑 |
|------|------|
| UseCase 定義 | [../examples/usecase/](../examples/usecase/) |
| BDD 測試範例 | [../examples/bdd-gherkin-test/](../examples/bdd-gherkin-test/) |
| UseCase 測試 | [../examples/use-case-test-example.md](../examples/use-case-test-example.md) |

---

## 相關文件

- [aggregate-standards.md](aggregate-standards.md)
- [mapper-standards.md](mapper-standards.md)
- [repository-standards.md](repository-standards.md)
- [projection-standards.md](projection-standards.md)
