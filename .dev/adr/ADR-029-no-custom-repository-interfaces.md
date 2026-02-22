# ADR-029: 禁止自定義 Repository 介面 (.NET)

## 狀態
已接受 (Accepted)

## 日期
2025-08-17

## 背景
發現專案中出現 `ProductRepository`、`SprintRepository` 等自定義 Repository 介面，雖然繼承 `IRepository<T, TId>` 但沒有新增方法。這違反 DDD/CQRS 原則並誘導濫用 Repository。

## 決策
**絕對禁止建立自定義 Repository 介面**。一律直接注入 `IRepository<Aggregate, AggregateId>`。

### 具體規範
1. **禁止**：`interface ProductRepository : IRepository<Product, ProductId>`
2. **必須**：直接注入 `IRepository<Product, ProductId>`
3. Repository 只提供三個標準方法：
   - `FindById`
   - `Save`
   - `Delete`
4. 查詢需求使用 Projection / Query Service

## 實施方案

### 1. 程式碼修正
```csharp
// ❌ 錯誤：自定義 Repository 介面
public interface IProductRepository : IRepository<Product, ProductId> { }

// ✅ 正確：直接使用 generic Repository
public class CreateProductService : ICreateProductUseCase
{
    private readonly IRepository<Product, ProductId> _repository;

    public CreateProductService(IRepository<Product, ProductId> repository)
    {
        _repository = repository;
    }
}
```

### 2. DI 註冊
```csharp
services.AddScoped<IRepository<Product, ProductId>, InMemoryProductRepository>();
services.AddScoped<ICreateProductUseCase, CreateProductService>();
```

### 3. 查詢處理
```csharp
public interface IProductDtoProjection
{
    List<ProductDto> FindByStatus(string status);
}
```

## 後果
- ✅ 架構簡潔
- ✅ CQRS 分離明確
- ✅ 避免 Repository 職責膨脹
- ⚠️ 開發者需適應規範

## 監控與執行
- 檢查腳本：`.ai/scripts/check-repository-compliance.sh`
- Code Review 必須檢查 Repository 介面

