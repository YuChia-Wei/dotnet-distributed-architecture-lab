# .NET AI 協作開發框架

這是 .NET 版 AI 協作開發框架，幫助團隊以 DDD + Clean Architecture + CQRS 交付高品質程式碼。

## 🎯 框架特色

- **DDD + Clean Architecture**：完整實作領域驅動設計與清潔架構
- **Sub-agent Workflow System**：專門的 AI sub-agents 處理不同類型任務
- **Event Sourcing + Outbox**：WolverineFx + EF Core
- **Profile-Based Testing**：支援 `test-inmemory` / `test-outbox`
- **BDD 測試**：xUnit + BDDfy（Gherkin 風格命名）

## 📚 核心文檔

### 必讀文檔
- **[INDEX.MD](INDEX.MD)** - .NET 文檔索引
- **[SUB-AGENT-SYSTEM.MD](SUB-AGENT-SYSTEM.MD)** - Sub-agent 工作流程
- **[CODE-REVIEW-INDEX.MD](CODE-REVIEW-INDEX.MD)** - Code Review 索引

### 學習路徑 (位於 .dev/guides/)
- [../../.dev/guides/](../../.dev/guides/)

## 📁 目錄結構

```
.ai/                    ← 純 AI 指令
├── INDEX.MD
├── README.MD
├── SUB-AGENT-SYSTEM.MD
├── CODE-REVIEW-INDEX.MD
├── prompts/
└── scripts/

.dev/                   ← 專案知識 (人機共用)
├── adr/
├── lessons/
├── guides/                    ← 學習指南
├── requirement/
├── specs/
└── standards/                 ← Code Review Checklist
```

## 🚀 快速開始

### 使用 Sub-agent Workflow
```
請使用 command-sub-agent workflow 實作 [create-product]
請使用 query-sub-agent workflow 實作 [get-product]
請使用 reactor-sub-agent workflow 實作 [notify-sprint-to-select-backlog-item]
請使用 aggregate-sub-agent workflow 實作 [ProductBacklogItem 狀態機]
請使用 outbox-sub-agent workflow 為 [Product] 實作 Outbox Pattern
請使用 mutation-testing-sub-agent workflow 為 [Product] 提升 mutation coverage
```

### 執行測試
```bash
dotnet test
ASPNETCORE_ENVIRONMENT=test-inmemory dotnet test
ASPNETCORE_ENVIRONMENT=test-outbox dotnet test
```

### 自動化檢查
```bash
.ai/scripts/check-all.sh
.ai/scripts/check-spec-compliance.sh <spec-file> <task-name>
.ai/scripts/check-mutation-coverage.sh
```

## ⚠️ 重要原則

1. **版本管理**：所有版本號以 `.dev/project-config.yaml` 為準
2. **Profile 測試**：支援 `test-inmemory` / `test-outbox` 雙 profile
3. **測試規範**：Use Case 測試必須使用 BDDfy（Gherkin 風格命名）
4. **Repository 規範**：絕對不要創建自定義 Repository 介面
5. **Outbox 規範**：OutboxMapper 必須是內部類別

## 📖 技術棧版本

請以 `.dev/project-config.yaml` 的版本為準（.NET 10 / C# 14 / WolverineFx / EF Core / xUnit / BDDfy / NSubstitute）。

---
**注意**：本框架為通用 .NET AI 協作範本，請勿放入專案特定內容。

