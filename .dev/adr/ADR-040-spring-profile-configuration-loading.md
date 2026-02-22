# ADR-040: .NET Environment Configuration Loading

## 狀態
已採用 (Adopted)

## 日期
2025-08-26

## 背景 (Context)
Outbox 測試需要不同的資料庫設定（PostgreSQL vs InMemory）。.NET 使用 `DOTNET_ENVIRONMENT` / `ASPNETCORE_ENVIRONMENT` 搭配 `appsettings.{Environment}.json` 管理環境配置，需要一致的命名與載入規則。

## 決策 (Decision)
採用 **`appsettings.{Environment}.json`** 的標準環境配置機制，不使用 `.feature` 或其他自製 Profile 系統。

## 詳細說明

### 1. 配置檔案命名規則
.NET 會自動載入：
- `appsettings.json`
- `appsettings.{Environment}.json`

環境由 `DOTNET_ENVIRONMENT` 或 `ASPNETCORE_ENVIRONMENT` 決定。

### 2. 檔案位置與優先順序
```
Solution
├── src/App/
│   ├── appsettings.json
│   ├── appsettings.Development.json
│   ├── appsettings.TestOutbox.json
│   └── appsettings.Production.json
└── tests/App.Tests/
    └── appsettings.TestOutbox.json   # 測試專用覆蓋
```

載入順序（後者覆蓋前者）：
1. `appsettings.json`
2. `appsettings.{Environment}.json`
3. 以 `AddJsonFile` 額外載入的測試覆蓋檔

### 3. 配置載入流程
```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Configuration
    .AddJsonFile("appsettings.json", optional: false)
    .AddJsonFile($"appsettings.{builder.Environment.EnvironmentName}.json", optional: true);
```

### 4. 實際應用範例
#### 基礎配置（appsettings.json）
```json
{
  "Repository": { "Mode": "InMemory" }
}
```

#### Outbox 測試配置（appsettings.TestOutbox.json）
```json
{
  "Repository": { "Mode": "Outbox" },
  "ConnectionStrings": {
    "MessageStore": "Host=localhost;Port=5800;Database=board;Username=postgres;Password=root"
  }
}
```

### 5. 多重環境切換
```bash
DOTNET_ENVIRONMENT=TestOutbox dotnet test
```

### 6. 驗證配置載入
```csharp
public class ProfileVerificationTests
{
    [Fact]
    public void should_load_correct_environment()
    {
        var env = Environment.GetEnvironmentVariable("DOTNET_ENVIRONMENT");
        Assert.Equal("TestOutbox", env);
    }
}
```

### 7. 最佳實踐
1. **命名一致性**：使用 PascalCase 環境名稱（`TestOutbox`）
2. **配置分離**：共用配置放 `appsettings.json`，環境差異放 `appsettings.{Environment}.json`
3. **測試隔離**：測試專用配置放在測試專案
4. **文件化**：在 README 標註可用的 Environment 名稱

## 效益 (Consequences)

### 優點
- ✅ 環境隔離清楚
- ✅ 配置重用與覆蓋簡單
- ✅ 測試彈性高

### 缺點
- ⚠️ 配置分散，需要清楚文件化
- ⚠️ 環境名稱錯誤會導致配置未載入

## 相關文件
- `ADR-019-outbox-pattern-implementation.md`
- `.dev/standards/examples/outbox/OUTBOX-TEST-CONFIGURATION.md`

