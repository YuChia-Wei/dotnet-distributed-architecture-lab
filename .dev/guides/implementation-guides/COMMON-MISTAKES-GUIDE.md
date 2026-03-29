# 常見錯誤與解決方案指南 (.NET)

> 本指南收集在 .NET DDD + WolverineFx + EF Core 開發中常見錯誤及其解決方案。

## 📋 目錄
1. [編譯錯誤](#編譯錯誤)
2. [測試錯誤](#測試錯誤)
3. [ASP.NET Core 錯誤](#aspnet-core-錯誤)
4. [EF Core 錯誤](#ef-core-錯誤)
5. [事件處理錯誤](#事件處理錯誤)
6. [Domain 模型錯誤](#domain-模型錯誤)

## 🔴 編譯錯誤

### 1. Cannot resolve symbol: DomainEvent
**原因**：缺少 ezDDD 概念對應的 .NET 基底類別/套件。

**解決方案**：
- 確認自定義的 DomainEvent 介面或基底類別已建立
- 確認專案參考與命名空間正確
- TODO: 補齊 .NET 版 ezddd 套件

### 2. Missing package reference
**解決方案**：
```bash
dotnet restore
dotnet add package WolverineFx
dotnet add package Microsoft.EntityFrameworkCore
```

## 🧪 測試錯誤

### 1. BDDfy 測試無法執行
**原因**：未引用 BDDfy 或未在測試方法中呼叫 `this.BDDfy()`。

**解決方案**：
- 確認測試專案已安裝 `TestStack.BDDfy`
- 確認測試方法內有呼叫 `this.BDDfy()`
- 確認 Given/When/Then 方法命名符合 Gherkin 風格

### 2. 使用 BaseTestClass
**解決方案**：禁止 BaseTestClass，改用 xUnit fixtures 或 DI helper。

## 🌐 ASP.NET Core 錯誤

### 1. DI 找不到服務
**解決方案**：
- 在 `Program.cs` 註冊 UseCase/Handler/Repository
- 確認介面與實作對應

### 2. Controller 直接依賴 Repository
**解決方案**：改為注入 UseCase/Handler，避免跨層依賴。

## 🗃️ EF Core 錯誤

### 1. Migration 未更新
**解決方案**：
```bash
dotnet ef migrations add <Name>
dotnet ef database update
```

### 2. Connection string 錯誤
**解決方案**：
- 檢查 `appsettings.json` 與環境變數
- 確認正確的 DB 連線字串與 schema

## 🔔 事件處理錯誤

### 1. Event 未被處理
**原因**：未註冊 WolverineFx handlers。

**解決方案**：
- 檢查 Wolverine 配置與 handler discovery
- 確認事件型別對應正確

## 🧩 Domain 模型錯誤

### 1. Aggregate 直接修改狀態
**解決方案**：改用 Apply/When 事件模式。

### 2. 未使用 DateProvider
**解決方案**：以 TimeProvider/DateProvider 取代 DateTime.UtcNow。
