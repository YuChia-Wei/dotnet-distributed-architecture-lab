# 資料庫遷移指南 (.NET)

## 📋 概述
本指南說明 .NET 版本的資料庫遷移策略與最佳實踐，目標是穩定、安全、可回滾。

## 🎯 遷移策略

### 工具選擇
1. **EF Core Migrations** - 標準做法（開發/測試/生產）
2. **DbUp / Flyway** - 進階或跨語言需求（視專案需求）

```
開發環境: EF Core Migrations
測試環境: EF Core Migrations + Testcontainers
生產環境: EF Core Migrations（產生 SQL 先審核）
```

## 🛠️ EF Core Migrations 設定

### 1. 必要套件
```bash
dotnet add package Microsoft.EntityFrameworkCore
dotnet add package Microsoft.EntityFrameworkCore.Design
dotnet add package Npgsql.EntityFrameworkCore.PostgreSQL
```

### 2. 目錄結構（建議）
```
src/Infrastructure/
└── Migrations/
    ├── 202401010900_InitialCreate.cs
    ├── 202401011030_AddUserTable.cs
    └── ...
```

### 3. 基本命令
```bash
# 建立遷移
dotnet ef migrations add InitialCreate --project src/Infrastructure --startup-project src/Api

# 套用遷移
dotnet ef database update --project src/Infrastructure --startup-project src/Api

# 產出 SQL（建議上線前審核）
dotnet ef migrations script --project src/Infrastructure --startup-project src/Api -o migration.sql
```

## 🔄 遷移程序

### 1. 開發/測試
```bash
dotnet ef migrations add AddPlanTables --project src/Infrastructure --startup-project src/Api
dotnet ef database update --project src/Infrastructure --startup-project src/Api
```

### 2. 生產環境（建議）
```bash
# 產生 SQL，手動審核後執行
dotnet ef migrations script --project src/Infrastructure --startup-project src/Api -o release.sql
```

## 🔁 回滾策略

### EF Core 回滾
```bash
# 回到上一個 migration
dotnet ef database update PreviousMigration --project src/Infrastructure --startup-project src/Api

# 回到初始狀態（僅限測試/開發）
dotnet ef database update 0 --project src/Infrastructure --startup-project src/Api
```

## 🎨 最佳實踐

1. **禁止在生產環境使用 EnsureCreated/EnsureDeleted**
2. **產出 SQL 後審核再上線**
3. **使用明確命名（含時間前綴）**
4. **重要變更要有回滾策略**
5. **Outbox / Event Store schema 必須納入遷移**

## 📊 監控與健康檢查

### Pending migrations
```csharp
public sealed class MigrationHealthCheck : IHealthCheck
{
    private readonly AppDbContext _db;
    public MigrationHealthCheck(AppDbContext db) => _db = db;

    public Task<HealthCheckResult> CheckHealthAsync(
        HealthCheckContext context, CancellationToken token = default)
    {
        var pending = _db.Database.GetPendingMigrations().ToList();
        return Task.FromResult(pending.Count == 0
            ? HealthCheckResult.Healthy()
            : HealthCheckResult.Degraded($"Pending migrations: {pending.Count}"));
    }
}
```

## 📋 檢查清單

### 遷移前
- [ ] 完整備份資料庫
- [ ] 測試環境驗證
- [ ] 準備回滾計畫

### 遷移後
- [ ] 驗證應用功能
- [ ] 檢查 pending migrations
- [ ] 監控效能指標
