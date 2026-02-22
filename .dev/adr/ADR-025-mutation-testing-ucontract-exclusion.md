# ADR-025: Mutation Testing 與 uContract 排除策略 (.NET)

## 狀態
已採納 (Accepted)

## 背景
在執行 **Stryker.NET** 變異測試時觀察到：

1. **uContract 產生大量無意義的變異**
   - 變異數量大幅增加，拉低 mutation score
2. **實際測試結果對比**
   - 排除 uContract 後，mutation score 與 test strength 更能反映業務邏輯覆蓋率
3. **uContract 的本質**
   - uContract 是 Design by Contract (DbC) 工具
   - 用於前置/後置條件與不變量
   - **不是業務邏輯**

## 決策

### 核心原則
1. **所有 mutation testing 必須排除 uContract 相關變異**
2. **uContract + 正確測試策略可取代部分冗餘斷言**

### Stryker.NET 配置規範（示意）
```json
{
  "stryker-config": {
    "project": "YourProject.csproj",
    "excluded-methods": [
      "BuildingBlocks.uContract.*",
      "UContract.*"
    ],
    "excluded-files": [
      "**/BuildingBlocks/uContract/**"
    ]
  }
}
```

### 測試策略
1. **Use Case Test + uContract**：透過 use case 測試觸發 Contract 檢查
2. **Unit Test + uContract**：直接測試 Aggregate 行為，Contract 自動驗證不變量
3. **Assertion-free Test**：依賴 Contract 進行驗證，減少冗餘斷言

## 原因

### 為什麼要排除 uContract
1. **Contract 不是被測試的對象**
2. **更準確的覆蓋率指標**
3. **減少測試噪音**

### Design by Contract 的價值
1. **Contract 即文檔**
2. **Runtime 驗證**
3. **提升程式品質**

## 影響
- ✅ Mutation score 更能反映實際測試品質
- ✅ 減少不必要測試工作量
- ✅ 鼓勵正確使用 DbC
- ⚠️ 團隊必須理解 DbC 概念
- ⚠️ CI 必須統一 Stryker.NET 配置

## 實施指南
1. **立即行動**
   - 更新 `stryker-config.json` 加入 uContract 排除
   - CI pipeline 統一使用 `dotnet stryker`
2. **團隊教育**
3. **監控指標**

## 實戰經驗與教訓 (2025-08-28 更新)

### 關鍵學習：增強既有程式碼的 Contract

#### ❌ 錯誤作法：一次性加入大量 Contract
```csharp
Require("Task name must be meaningful",
    () => name.Trim().Length is >= 3 and <= 200);
Require("PBI must be in valid state for task creation",
    () => state is PbiState.Selected or PbiState.InProgress);
Require("Valid state transition",
    () => IsValidStateTransition(fromState, newState));
```
**結果**：既有測試失敗，因為新 Contract 改變了既有行為。

#### ✅ 正確作法：漸進式加入 Contract
```csharp
Require("Task name must not be empty", () => !string.IsNullOrWhiteSpace(name));
Require("Cannot create duplicate task",
    () => tasks.All(t => t.Id != taskId));
Ensure("Task is in the task list",
    () => tasks.Any(t => t.Id == taskId));
```

### 實施原則
1. **理解既有行為**：Contract 應該描述而非改變行為
2. **漸進式實施**：一次只加一個小 Contract，立即測試
3. **Contract 優先順序**：postconditions → invariants → preconditions
4. **與測試協同演進**：Contract 不應破壞既有測試

### 建議工作流程
```bash
# 1. 執行基準測試
dotnet test

# 2. 加入一個 Contract，立即測試
dotnet test

# 3. 變異測試
dotnet stryker
```

## 參考資料
- Design by Contract
- Stryker.NET
- uContract

