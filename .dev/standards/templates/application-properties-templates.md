# ASP.NET Core appsettings 模板集 🔧

## 🎯 Purpose
提供完整的 `appsettings.json` 與 `appsettings.{Environment}.json` 模板，避免 Profile 與連線設定錯誤。

## 📋 配置檔案結構

```
src/Api/
├── appsettings.json                # 主配置
├── appsettings.InMemory.json       # InMemory Profile
├── appsettings.Outbox.json         # Outbox Profile
├── appsettings.Test.json           # 測試主配置
├── appsettings.Test-InMemory.json  # InMemory 測試
└── appsettings.Test-Outbox.json    # Outbox 測試
```

## 1️⃣ appsettings.json（主配置）

```json
{
  "App": {
    "Name": "ai-scrum"
  },
  "Profiles": {
    "Mode": "InMemory"
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft": "Warning",
      "Microsoft.AspNetCore": "Warning"
    }
  }
}
```

## 2️⃣ appsettings.InMemory.json（InMemory Profile）

```json
{
  "Profiles": {
    "Mode": "InMemory"
  },
  "Persistence": {
    "Provider": "InMemory"
  }
}
```

## 3️⃣ appsettings.Outbox.json（Outbox Profile）

```json
{
  "Profiles": {
    "Mode": "Outbox"
  },
  "Persistence": {
    "Provider": "PostgreSQL"
  },
  "ConnectionStrings": {
    "MainDb": "Host=localhost;Port=5432;Database=aiscrum;Username=postgres;Password=root"
  },
  "Outbox": {
    "PollingIntervalMs": 5000,
    "BatchSize": 100
  }
}
```

## 4️⃣ appsettings.Test.json（測試主配置）

```json
{
  "Profiles": {
    "Mode": "Test-InMemory"
  },
  "Logging": {
    "LogLevel": {
      "Default": "Warning"
    }
  }
}
```

## 5️⃣ appsettings.Test-InMemory.json（InMemory 測試）

```json
{
  "Profiles": {
    "Mode": "Test-InMemory"
  },
  "Persistence": {
    "Provider": "InMemory"
  }
}
```

## 6️⃣ appsettings.Test-Outbox.json（Outbox 測試）

```json
{
  "Profiles": {
    "Mode": "Test-Outbox"
  },
  "Persistence": {
    "Provider": "PostgreSQL"
  },
  "ConnectionStrings": {
    "MainDb": "Host=localhost;Port=5800;Database=testdb;Username=postgres;Password=root"
  }
}
```

## 🚨 關鍵配置解釋

### 1. 為什麼需要 Profiles/Mode？
Profile 用於切換 InMemory / Outbox 行為，避免多套配置衝突。

### 2. Profile 命名規範
- `InMemory`
- `Outbox`
- `Test-InMemory`
- `Test-Outbox`

### 3. 資料庫 Port 分離
- 開發環境：5432
- 測試環境：5800

## 🔍 診斷命令

```bash
# 檢查環境變數
echo $ASPNETCORE_ENVIRONMENT

# 使用指定環境啟動
ASPNETCORE_ENVIRONMENT=Outbox dotnet run --project src/Api
```

## ⚠️ 常見錯誤與解決

### 錯誤 1：未載入正確 appsettings.{Environment}.json
**解決**：確認 `ASPNETCORE_ENVIRONMENT` 正確設定。

### 錯誤 2：Repository 無法解析
**解決**：確認對應 profile 的 DI 註冊存在。

## 📝 最佳實踐

1. 先用 InMemory Profile 開發
2. Outbox Profile 需對應資料庫
3. 測試時明確指定 Profile
4. Production 以環境變數覆蓋敏感設定
