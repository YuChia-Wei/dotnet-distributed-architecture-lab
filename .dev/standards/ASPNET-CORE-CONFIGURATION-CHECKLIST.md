# ASP.NET Core 配置檢查清單 🔥

## ⚠️ 必須避免的常見錯誤

本清單記錄在 .NET 版本中常見的設定錯誤，避免重複踩雷。

## 1. 資料庫連線配置

### ❌ 錯誤：使用錯誤的 port
```json
// 錯誤
"MainDb": "Host=localhost;Port=5500;Database=app;Username=app;Password=app"

// 正確
"MainDb": "Host=localhost;Port=5432;Database=app;Username=app;Password=app"
```

### ❌ 錯誤：schema 配置方式錯誤
```json
// 錯誤：未指定 schema 或使用錯誤鍵
"MainDb": "Host=localhost;Port=5432;Database=app;Username=app;Password=app"

// 正確：在連線字串指定 schema
"MainDb": "Host=localhost;Port=5432;Database=app;Username=app;Password=app;Search Path=message_store"
```

## 2. 套件依賴配置

### ❌ 錯誤：漏裝 provider
- 缺少 `Microsoft.EntityFrameworkCore.Npgsql` 或 `Microsoft.EntityFrameworkCore.SqlServer`

### ✅ 正確做法
```bash
dotnet add package Microsoft.EntityFrameworkCore
dotnet add package Npgsql.EntityFrameworkCore.PostgreSQL
```

## 3. Profile / Environment 配置

### ❌ 錯誤：未建立 appsettings.{Environment}.json
必須建立 `appsettings.InMemory.json` / `appsettings.Outbox.json`（或對應名稱）。

### ✅ 正確做法
- `ASPNETCORE_ENVIRONMENT=InMemory` / `Outbox`
- 使用 `IConfiguration` 讀取 Profile
- 不要再建立另一套自製 profile 機制
- 環境命名維持一致，例如 `TestInMemory` / `TestOutbox`

### ✅ 規範來源
- 詳細硬規則以 `coding-standards/profile-configuration-standards.md` 為準

## 4. WolverineFx 配置

### ❌ 錯誤：未註冊 handlers / messaging
**解法**：檢查 WolverineFx 服務註冊與 assembly 掃描。

## 5. EF Core Migration

### ❌ 錯誤：Migration 未更新或未套用
```bash
dotnet ef migrations add Init
dotnet ef database update
```
