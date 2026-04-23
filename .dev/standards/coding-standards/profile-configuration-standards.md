# Profile / Environment Configuration Standards (.NET)

本文件定義 profile、environment、以及 profile-specific DI 的硬性規則。
本文件收斂 environment loading 與 profile-specific dependency injection 的正式規則。

使用方式教學與排錯流程，應放在 `.dev/guides/implementation-guides/`，不要把操作教學混進這份標準。

---

## 🔴 必須遵守的規則 (MUST FOLLOW)

### 1. 環境只能由 `DOTNET_ENVIRONMENT` 或 `ASPNETCORE_ENVIRONMENT` 決定

不得引入自製 profile 切換機制，例如 `.feature`、自訂 profile 字串拼接、或在程式內硬編碼覆蓋目前環境。

```csharp
// ✅ 正確：由 Host/Builder 提供當前環境
var builder = WebApplication.CreateBuilder(args);
var environmentName = builder.Environment.EnvironmentName;

builder.Configuration
    .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true)
    .AddJsonFile($"appsettings.{environmentName}.json", optional: true, reloadOnChange: true);
```

```csharp
// ❌ 錯誤：自行建立另一套 profile 系統
var profile = configuration["Profile"] ?? "outbox";
builder.Configuration.AddJsonFile($"appsettings.{profile}.json");
```

### 2. Profile 差異必須放在 `appsettings.{Environment}.json`

共用設定放 `appsettings.json`，環境差異放 `appsettings.{Environment}.json`。
不要把某個特定 profile 的值硬寫回基礎 `appsettings.json`。

```json
// ✅ 正確：共用設定
{
  "Repository": {
    "Mode": "InMemory"
  }
}
```

```json
// ✅ 正確：TestOutbox 差異只放在環境檔
{
  "Repository": {
    "Mode": "Outbox"
  },
  "ConnectionStrings": {
    "Outbox": "Host=localhost;Port=5432;Database=app_test;Username=postgres;Password=root"
  }
}
```

### 3. Environment 名稱必須一致且可預測

- 使用單一命名慣例，不混用多種大小寫與別名
- 目前標準命名：
  - `Development`
  - `Production`
  - `InMemory`
  - `Outbox`
  - `TestInMemory`
  - `TestOutbox`

```bash
# ✅ 正確
DOTNET_ENVIRONMENT=TestOutbox dotnet test

# ❌ 錯誤：混用自製 profile 與多值
DOTNET_ENVIRONMENT=test,test-outbox dotnet test
```

### 4. Profile-specific DI 必須在 Composition Root 明確分支

環境差異的 DI 註冊必須集中在 composition root 或 profile-specific registration module。
禁止依賴 attribute scanning、自動 assembly 掃描、或在任意類別內偷偷切 profile。

```csharp
// ✅ 正確：集中在 composition root 分支
if (builder.Environment.IsEnvironment("TestOutbox") || builder.Environment.IsEnvironment("Outbox"))
{
    services.AddDbContext<AppDbContext>(...);
    services.AddScoped<IRepository<Product, ProductId>, OutboxProductRepository>();
}
else
{
    services.AddSingleton<IRepository<Product, ProductId>, InMemoryProductRepository>();
}
```

### 5. InMemory profile 不得註冊 EF Core / Npgsql 依賴

InMemory 與 TestInMemory profile 必須能在沒有 DbContext、Npgsql、或 durable outbox 的情況下啟動。

```csharp
// ❌ 錯誤：InMemory profile 仍註冊 DbContext
services.AddDbContext<AppDbContext>(...);
```

### 6. Outbox profile 必須完整註冊 persistence chain

Outbox 與 TestOutbox profile 必須完整包含：

- DbContext
- Outbox / Wolverine persistence
- 對應 repository 實作

禁止只有部分註冊，導致 runtime 啟動成功但執行時失敗。

### 7. 應依賴抽象，不得在一般服務 constructor 綁定特定 profile 的 infra 類型

```csharp
// ✅ 正確：依賴抽象
public sealed class TestDataInitializer
{
    private readonly IRepository<Product, ProductId> _repository;

    public TestDataInitializer(IRepository<Product, ProductId> repository)
    {
        _repository = repository;
    }
}
```

```csharp
// ❌ 錯誤：直接綁定特定 infra
public sealed class TestDataInitializer
{
    public TestDataInitializer(AppDbContext dbContext)
    {
    }
}
```

### 8. 測試不得在測試類別內動態竄改全域 environment 狀態

Profile 選擇應在 test host、fixture、或執行命令層完成，不要在測試類別內直接覆蓋全域 environment variable。

---

## 檢查清單

- [ ] 只使用 `DOTNET_ENVIRONMENT` / `ASPNETCORE_ENVIRONMENT`
- [ ] 使用 `appsettings.{Environment}.json` 管理環境差異
- [ ] Environment 名稱遵守既定命名
- [ ] DI profile 分支集中於 composition root
- [ ] InMemory profile 沒有 EF Core / Npgsql 註冊
- [ ] Outbox profile 有完整 persistence chain
- [ ] 一般服務依賴抽象，不直接依賴特定 infra 類型
- [ ] 測試不在類別內修改全域 environment 狀態

---

## 相關文件

- [../../guides/implementation-guides/PROFILE-CONFIGURATION-COMPLEXITY-SOLUTION.md](../../guides/implementation-guides/PROFILE-CONFIGURATION-COMPLEXITY-SOLUTION.md)
- [../../guides/implementation-guides/DOTNET-DI-TEST-GUIDE.md](../../guides/implementation-guides/DOTNET-DI-TEST-GUIDE.md)
- [../ASPNET-CORE-CONFIGURATION-CHECKLIST.md](../ASPNET-CORE-CONFIGURATION-CHECKLIST.md)
