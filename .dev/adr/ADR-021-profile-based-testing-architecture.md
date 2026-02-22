# ADR-021: Profile-Based Testing Architecture (.NET)

## Status
Accepted

## Context
測試環境需要支援多種執行模式：
- InMemory：快速執行，適合 CI/CD
- Outbox：完整整合測試，使用真實 PostgreSQL

過去曾在 **Base Test Class** 內硬編碼環境，導致無法動態切換。該做法在 .NET 也不可接受。

## Decision
**絕對不要在任何 Base Test Class 中硬編碼環境設定**。  
環境選擇應由 **環境變數 + appsettings** 決定。

## Implementation

### ❌ 錯誤做法（禁止）
```csharp
public abstract class BaseUseCaseTest
{
    static BaseUseCaseTest()
    {
        Environment.SetEnvironmentVariable("DOTNET_ENVIRONMENT", "TestOutbox");
    }
}
```

### ✅ 正確做法
- **不使用 Base Test Class**
- 由測試執行命令或 CI Pipeline 設定環境：
```bash
DOTNET_ENVIRONMENT=TestOutbox dotnet test
```

### Profile / Environment 來源優先順序
1. 環境變數：`DOTNET_ENVIRONMENT` / `ASPNETCORE_ENVIRONMENT`
2. `appsettings.{Environment}.json`
3. 測試專案額外 `AddJsonFile` 覆蓋（必要時）

### 執行範例
```bash
# InMemory（預設）
dotnet test

# Outbox（PostgreSQL）
DOTNET_ENVIRONMENT=TestOutbox dotnet test
```

## Consequences

### Positive
- 測試可以在不同環境執行而不需改程式碼
- 同一個測試可驗證 in-memory 與 outbox 兩種實作

### Negative
- 需要正確設定環境變數
- 環境來源不清楚時容易混淆

## Lessons Learned
🔴 **重要教訓**：不要在測試程式碼中硬寫環境選擇。
- Profile 必須可配置
- 動態 > 靜態

