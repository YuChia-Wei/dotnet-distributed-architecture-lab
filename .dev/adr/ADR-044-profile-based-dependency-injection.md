# ADR-044: Profile-Based Dependency Injection 規範 (.NET)

## Status
Accepted

## Date
2025-09-07

## Context
InMemory / Outbox 雙軌架構下，不同環境有不同基礎設施依賴。若強制注入特定依賴，會導致某些環境無法啟動。

## Decision
建立以下規範，避免環境依賴衝突：

### 1. 條件化 DI 註冊
```csharp
if (env.IsEnvironment("TestOutbox"))
{
    services.AddDbContext<AppDbContext>(...);
    services.AddScoped<IRepository<,>, OutboxRepository<,>>();
}
else
{
    services.AddSingleton<IRepository<,>, InMemoryRepository<,>>();
}
```

### 2. 避免在 Constructor 強制依賴特定環境元件
```csharp
// ✅ 正確：依賴抽象
public class TestDataInitializer
{
    private readonly IRepository<Product, ProductId> _repo;
    public TestDataInitializer(IRepository<Product, ProductId> repo) { _repo = repo; }
}

// ❌ 錯誤：直接依賴 DbContext / Npgsql
public class TestDataInitializer
{
    public TestDataInitializer(AppDbContext db) { }
}
```

### 3. Runtime 防護
```csharp
if (_dbContext is null)
{
    _logger.LogInformation("DbContext not available, skipping cleanup.");
    return;
}
```

## Consequences
- ✅ 不同環境可獨立運行
- ✅ 減少啟動錯誤
- ✅ 架構更彈性
- ⚠️ 需要清楚環境差異

## Implementation Checklist
1. 建立 `appsettings.{Environment}.json`
2. 明確註冊差異 DI
3. 避免 constructor 綁定特定 infra
4. 加入 runtime 防護

## References
- ADR-021: Profile-Based Testing Architecture
- ADR-040: Environment Configuration Loading
