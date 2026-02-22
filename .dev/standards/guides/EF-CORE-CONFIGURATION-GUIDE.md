# EF Core Configuration Guide

## 🎯 核心原則

所有 EF Core 相關的 Repository/Projection/Inquiry/Archive 必須在 DI 中正確註冊，
並維持 DDD/CA/CQRS 分層：Domain 不依賴 EF Core，Infrastructure 才能使用 DbContext。

## 📦 結構建議

```
src/Infrastructure/
├── Repositories/Outbox/
├── Projections/
├── Inquiry/
└── Archive/
```

## 🔧 DbContext 設定

```csharp
builder.Services.AddDbContext<AppDbContext>(options =>
{
    var conn = builder.Configuration.GetConnectionString("MainDb");
    options.UseNpgsql(conn);
});
```

## 🧩 DI 註冊規則

- Repository / Projection / Inquiry / Archive 都必須註冊於 DI
- 只在 Infrastructure 註冊 DbContext
- Domain 與 Application 不可直接依賴 DbContext

```csharp
services.AddScoped<IPlanProjection, EfPlanProjection>();
services.AddScoped<IPlanArchive, EfPlanArchive>();
```

## ⚠️ 常見問題

### 問題 1: 無法解析服務
**錯誤訊息**：
```
Unable to resolve service for type 'EfPlanProjection'
```

**解決方案**：
- 確認類別已註冊到 DI
- 確認 namespace 與組件掃描一致

### 問題 2: 重複註冊
**症狀**：多個實作導致衝突

**解決方案**：
- 一個介面只對應一個實作
- InMemory/Outbox 需 profile 隔離註冊

## 🔍 自動檢查

```bash
# TODO: Rename legacy script name to check-ef-projection-config.sh.
.ai/scripts/check-jpa-projection-config.sh
```

> Note: Script name is legacy; keep it until the rename is completed.

## 📋 檢查清單

- [ ] Repository/Projection/Inquiry/Archive 已註冊
- [ ] DbContext 只在 Infrastructure 層使用
- [ ] Projection 使用 AsNoTracking
- [ ] 避免 Controller 直接依賴 DbContext
