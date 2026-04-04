# Repository 編碼規範 (.NET)

本文件定義 Repository 的編碼標準，包含介面設計、實作原則、EF Core Entity 設計等規範。

> **Projection 規範**: 複雜查詢相關規範請參考 [Projection 編碼規範](./projection-standards.md)

---

## 📌 概述

Repository 只負責 Aggregate 的基本存取（Command Side），查詢需求需透過 Query Repository + Query Service（Query Side）。

- **Repository 五個方法**：`FindByIdAsync`, `FindByIdsAsync`, `SaveAsync`, `SaveAllAsync`, `DeleteAsync`
- **禁止自定義查詢方法**：複雜查詢使用 Query Repository + Query Service
- **將讀寫模型分離**：Domain Repository 用於 Write Model，Query Repository 用於 Read Model

> 📖 模式理由詳見 [../../standards/rationale/query-side-layering-rationale.MD](../../standards/rationale/query-side-layering-rationale.MD)

---

## 🏷️ Pattern 標記（自動化檢查用）

以下標記供自動化 Code Review 腳本使用：

```yaml
# Repository 規則
Pattern (required, any): IDomainRepository<

# 允許的方法
Pattern (allowed): FindByIdAsync|FindByIdsAsync|SaveAsync|SaveAllAsync|DeleteAsync

# 禁止規則（Repository 不應有自定義查詢）
Pattern (forbidden, i): GetBy|QueryBy|SearchBy|FindByName|FindByStatus
```

---

## 🔴 必須遵守的規則 (MUST FOLLOW)

### 1. Repository Interface 設計

使用泛型 Repository Interface：

```csharp
// ✅ 正確：定義泛型 Repository Interface
namespace Lab.BuildingBlocks.Application;

public interface IDomainRepository<TAggregate, TId>
    where TAggregate : AggregateRoot<TId>
{
    // 基本操作
    Task<TAggregate?> FindByIdAsync(TId id, CancellationToken ct = default);
    Task SaveAsync(TAggregate aggregate, CancellationToken ct = default);
    Task DeleteAsync(TAggregate aggregate, CancellationToken ct = default);

    // 批次操作（效能優化，語意相同）
    Task<IReadOnlyList<TAggregate>> FindByIdsAsync(IEnumerable<TId> ids, CancellationToken ct = default);
    Task SaveAllAsync(IEnumerable<TAggregate> aggregates, CancellationToken ct = default);
}

// 在 Handler 中使用
public sealed class CreateProductHandler
{
    private readonly IDomainRepository<Product, ProductId> _repository;

    public CreateProductHandler(IDomainRepository<Product, ProductId> repository)
    {
        _repository = repository;
    }
}

// ❌ 錯誤：為每個 Aggregate 創建特定 Interface 加入額外方法
public interface IProductRepository : IDomainRepository<Product, ProductId>
{
    Task<Product?> GetByNameAsync(string name);  // ❌ 不應該加入查詢方法
}
```

---

### 2. Repository 實作 (EF Core)

```csharp
// ✅ 正確：Product Repository 實作
public class ProductRepository : IRepository<Product, ProductId>
{
    private readonly ApplicationDbContext _context;

    public ProductRepository(ApplicationDbContext context)
    {
        _context = context;
    }

    public async Task<Product?> FindByIdAsync(ProductId id, CancellationToken ct = default)
    {
        var data = await _context.Products
            .AsNoTracking()
            .FirstOrDefaultAsync(x => x.Id == id.Value, ct);

        return data is null ? null : ProductMapper.ToDomain(data);
    }

    public async Task SaveAsync(Product aggregate, CancellationToken ct = default)
    {
        var data = ProductMapper.ToData(aggregate);

        var existing = await _context.Products
            .FirstOrDefaultAsync(x => x.Id == data.Id, ct);

        if (existing is null)
        {
            await _context.Products.AddAsync(data, ct);
        }
        else
        {
            _context.Entry(existing).CurrentValues.SetValues(data);
        }

        aggregate.ClearDomainEvents();
    }

    public async Task DeleteAsync(Product aggregate, CancellationToken ct = default)
    {
        var data = await _context.Products
            .FirstOrDefaultAsync(x => x.Id == aggregate.Id.Value, ct);

        if (data is not null)
        {
            _context.Products.Remove(data);
        }

        aggregate.ClearDomainEvents();
    }
}
```

---

### 3. InMemory Repository（測試用）

```csharp
// ✅ 正確：InMemory Repository 實作
public class InMemoryRepository<TAggregate, TId> : IRepository<TAggregate, TId>
    where TAggregate : AggregateRoot<TId>
{
    private readonly Dictionary<TId, TAggregate> _store = new();

    public Task<TAggregate?> FindByIdAsync(TId id, CancellationToken ct = default)
    {
        _store.TryGetValue(id, out var aggregate);
        return Task.FromResult(aggregate);
    }

    public Task SaveAsync(TAggregate aggregate, CancellationToken ct = default)
    {
        _store[aggregate.Id] = aggregate;
        aggregate.ClearDomainEvents();
        return Task.CompletedTask;
    }

    public Task DeleteAsync(TAggregate aggregate, CancellationToken ct = default)
    {
        _store.Remove(aggregate.Id);
        aggregate.ClearDomainEvents();
        return Task.CompletedTask;
    }
}
```

---

### 4. DI 註冊

```csharp
// ✅ 正確：在 Program.cs 或 ServiceExtensions 中註冊
public static class RepositoryServiceExtensions
{
    public static IServiceCollection AddRepositories(this IServiceCollection services)
    {
        services.AddScoped<IRepository<Product, ProductId>, ProductRepository>();
        services.AddScoped<IRepository<Sprint, SprintId>, SprintRepository>();
        services.AddScoped<IRepository<ProductBacklogItem, PbiId>, PbiRepository>();

        return services;
    }
}
```

---

## 🎯 EF Core Entity (Data Model) 設計

### Entity 結構

```csharp
// ✅ 正確：EF Core Entity 設計
namespace YourProject.Infrastructure.Persistence.Entities;

public class ProductData
{
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string State { get; set; } = string.Empty;
    public string CreatorId { get; set; } = string.Empty;
    public bool IsDeleted { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }

    // 複雜物件序列化為 JSON
    public string? DefinitionOfDoneJson { get; set; }
    public string? TagsJson { get; set; }

    // 導航屬性（如需要）
    public List<TaskData> Tasks { get; set; } = new();

    // 樂觀鎖
    public byte[] RowVersion { get; set; } = Array.Empty<byte>();
}
```

### Fluent Configuration

```csharp
// ✅ 正確：使用 Fluent API 配置
public class ProductDataConfiguration : IEntityTypeConfiguration<ProductData>
{
    public void Configure(EntityTypeBuilder<ProductData> builder)
    {
        builder.ToTable("products");

        builder.HasKey(x => x.Id);

        builder.Property(x => x.Id)
            .HasColumnName("product_id")
            .HasMaxLength(50)
            .IsRequired();

        builder.Property(x => x.Name)
            .HasMaxLength(100)
            .IsRequired();

        builder.Property(x => x.IsDeleted)
            .IsRequired();

        builder.Property(x => x.RowVersion)
            .IsRowVersion();

        // 索引
        builder.HasIndex(x => x.Name);
        builder.HasIndex(x => x.State);

        // 軟刪除過濾
        builder.HasQueryFilter(x => !x.IsDeleted);
    }
}
```

---

## 🎯 Query Side 分層（嚴格 CQRS）

查詢操作採用 **Query Repository + Query Service** 雙層設計。

### 介面與實作放置位置

| 類型 | 介面位置 | 實作位置 |
|------|---------|---------|
| `IDomainRepository<T, TId>` | `BuildingBlocks.Application` | `<Domain>.Infrastructure/Repositories` |
| `I<Domain>QueryRepository` | `<Domain>.Applications/Ports` | `<Domain>.Infrastructure/QueryRepositories` |
| `I<Domain>QueryService` | `<Domain>.Applications/Ports` | `<Domain>.Applications/QueryServices` |

### Query Repository（Infrastructure 層）

```csharp
// ✅ 正確：Query Repository - 純資料存取，回傳 DTO/ID
public interface IProductQueryRepository
{
    Task<ProductDto?> GetByIdAsync(Guid productId, CancellationToken ct = default);
    Task<IReadOnlyList<ProductDto>> GetByStateAsync(string state, CancellationToken ct = default);
    Task<IReadOnlyList<Guid>> GetIdsByStateAsync(string state, CancellationToken ct = default);
}
```

| 規則 | 說明 |
|------|------|
| ✅ 允許 | 回傳 DTO、ID 列表 |
| ✅ 允許 | 使用 Dapper 或 EF Core Projection |
| ❌ 禁止 | 包含業務邏輯 |
| ❌ 禁止 | 回傳 Aggregate |

### Query Service（Application 層）

```csharp
// ✅ 正確：Query Service - 查詢業務邏輯
public interface IProductQueryService
{
    // 組合多個 Repository 查詢
    Task<ProductWithDetailsDto> GetProductWithDetailsAsync(Guid productId, CancellationToken ct = default);

    // 提供 IDs 給 Command Handler 使用
    Task<IReadOnlyList<Guid>> GetActiveProductIdsAsync(CancellationToken ct = default);
}
```

| 規則 | 說明 |
|------|------|
| ✅ 允許 | 組合多個 Query Repository |
| ✅ 允許 | 包含計算、轉換邏輯 |
| ✅ 允許 | 回傳 ID 列表供 Command 使用 |
| ❌ 禁止 | 直接存取資料庫 |
| ❌ 禁止 | 回傳 Aggregate |

---

## 🎯 事務管理

### 使用 IUnitOfWork

```csharp
// ✅ 正確：定義 IUnitOfWork
public interface IUnitOfWork
{
    Task<int> CommitAsync(CancellationToken ct = default);
}

// EF Core 實作
public class EfCoreUnitOfWork : IUnitOfWork
{
    private readonly DbContext _context;

    public EfCoreUnitOfWork(DbContext context)
    {
        _context = context;
    }

    public Task<int> CommitAsync(CancellationToken ct = default)
    {
        return _context.SaveChangesAsync(ct);
    }
}

// 在 Handler 中使用
public sealed class CreateProductHandler
{
    private readonly IRepository<Product, ProductId> _repository;
    private readonly IUnitOfWork _unitOfWork;

    public async Task<Result<ProductId>> Handle(
        CreateProductCommand command,
        CancellationToken ct)
    {
        var product = new Product(...);

        await _repository.SaveAsync(product, ct);
        await _unitOfWork.CommitAsync(ct);  // 提交交易

        return Result.Success(product.Id);
    }
}
```

---

## 🎯 效能優化

### 使用 AsNoTracking

```csharp
// ✅ 正確：只讀查詢使用 AsNoTracking
public async Task<Product?> FindByIdAsync(ProductId id, CancellationToken ct)
{
    var data = await _context.Products
        .AsNoTracking()  // 提升效能
        .FirstOrDefaultAsync(x => x.Id == id.Value, ct);

    return data is null ? null : ProductMapper.ToDomain(data);
}
```

---

## 🔍 檢查清單

### Repository Interface
- [ ] 使用泛型 `IRepository<TAggregate, TId>`
- [ ] 只有三個基本方法
- [ ] 透過 DI 註冊

### Repository 實作
- [ ] 使用 EF Core
- [ ] 呼叫 `ClearDomainEvents()` 在 Save/Delete 後
- [ ] 使用 `AsNoTracking()` 於只讀查詢

### EF Core Entity
- [ ] 使用 Fluent API 配置
- [ ] 有主鍵
- [ ] 有樂觀鎖 (RowVersion)
- [ ] 有軟刪除過濾 (`HasQueryFilter`)
- [ ] 有必要的索引

### 效能
- [ ] 避免 N+1 查詢
- [ ] 使用 `Include` 預載
- [ ] 支援分頁查詢

---

## 📂 程式碼範例

更多完整範例請參考：

| 範例 | 路徑 |
|------|------|
| Outbox + Repository 範例 | [../examples/outbox/](../examples/outbox/) |
| Profile Configs 範例 | [../examples/profile-configs/](../examples/profile-configs/) |

---

## 相關文件

- [aggregate-standards.md](aggregate-standards.md)
- [mapper-standards.md](mapper-standards.md)
- [projection-standards.md](projection-standards.md)
