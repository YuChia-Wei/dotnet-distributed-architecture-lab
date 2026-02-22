# Sub-agent System Architecture (.NET)

本文件定義 .NET Sub-agent 系統架構，適用於 WolverineFx + EF Core + xUnit + BDDfy。

## 🎯 系統目標

1. 降低認知負擔（每個 agent 專注特定領域）
2. 提高規範遵守率（專注 context）
3. 降低錯誤率（避免跨領域混用規則）
4. 提升輸出品質（可重複、可驗證）

## 🤖 Sub-agent 角色定義

### Use Case Sub-agents（Command / Query）

#### 1a. Command Code Generation Agent
- **職責**：產生 Command use case 的 production code
- **專注領域**：Aggregate 狀態變更、Domain Events、Repository Save、事務一致性
- **架構感知**：依 `.dev/project-config.yaml` 決定 InMemory / Outbox / Event Sourcing 模式
- **Outbox 模式**：必須產生 Data / Mapper / OutboxRepository
- **Prompt**：`.ai/prompts/command-sub-agent-prompt.md`

#### 1b. Query Code Generation Agent
- **職責**：產生 Query use case 的 production code
- **專注領域**：Projection 設計、DTO mapping、Read model
- **Prompt**：`.ai/prompts/query-sub-agent-prompt.md`

#### 2. Test Generation Agent
- **職責**：產生測試程式碼
- **專注領域**：xUnit + BDDfy（Gherkin 風格命名）、NSubstitute
- **限制**：禁止 BaseTestClass
- **Prompt**：`.ai/prompts/usecase-test-generation-prompt.md`

#### 3. Code Review Agent
- **職責**：審查程式碼品質與規範遵守
- **Prompt**：`.ai/prompts/code-review-prompt.md`

### Testing Enhancement Sub-agents

#### 4. Contract Test Generation Agent
- **職責**：產生 Aggregate Contract Tests（DBC preconditions）
- **Prompt**：`.ai/prompts/contract-test-generation-prompt.md`

#### 5. Mutation Testing Enhancement Agent
- **職責**：Stryker.NET + uContract + assertion-free tests
- **Prompt**：`.ai/prompts/mutation-testing-sub-agent-prompt.md`
- **腳本**：`.ai/scripts/check-mutation-coverage.sh`

### Controller Sub-agents

#### 6. Controller Code Generation Agent
- **Prompt**：`.ai/prompts/controller-code-generation-prompt.md`

#### 7. Controller Test Generation Agent
- **Prompt**：`.ai/prompts/controller-test-generation-prompt.md`

#### 8. Controller Code Review Agent
- **Prompt**：`.ai/prompts/controller-code-review-prompt.md`

### Aggregate Sub-agents

#### 9. Aggregate Code Generation Agent
- **Prompt**：`.ai/prompts/aggregate-sub-agent-prompt.md`

#### 10. Aggregate Test Generation Agent
- **Prompt**：`.ai/prompts/aggregate-test-generation-prompt.md`

#### 11. Aggregate Code Review Agent
- **Prompt**：`.ai/prompts/aggregate-code-review-prompt.md`

### Reactor Sub-agents

#### 12. Reactor Code Generation Agent
- **職責**：跨聚合事件處理 / Read model projection / MQ integration
- **Prompt**：`.ai/prompts/reactor-sub-agent-prompt.md`

#### 13. Reactor Test Generation Agent
- **Prompt**：`.ai/prompts/reactor-test-generation-prompt.md`

#### 14. Reactor Code Review Agent
- **Prompt**：`.ai/prompts/reactor-code-review-prompt.md`

### Reconciler Sub-agents

#### 15. Reconciler Code Generation Agent
- **職責**：定期校正跨聚合狀態漂移（Scheduler 驅動）
- **核心要求**：入口 `reconcile()`、idempotent、跨聚合查詢
- **Prompt**：`.ai/prompts/reconciler-sub-agent-prompt.md`（TODO：尚未建立）

### Specification Sub-agents

#### 16. Problem Frame Sub-agent
- **職責**：從 Problem Frame 規格產生完整功能
- **來源**：`.dev/problem-frames/*.yaml`（若未存在，請標記 TODO）
- **要求**：Spec compliance 100% gate
- **Prompt**：`.ai/prompts/problem-frame-sub-agent-prompt.md`（若尚未建立，請標記 TODO）

### Infrastructure Sub-agents

#### 17. Profile Configuration Agent
- **職責**：設定 `test-inmemory` / `test-outbox` profiles
- **重點**：profile 完全隔離、EF Core 註冊分離
- **Prompt**：`.ai/prompts/profile-config-sub-agent-prompt.md`

#### 18. Outbox Pattern Implementation Agent
- **職責**：OutboxData / OutboxMapper / Repository 配置
- **重點**：`IOutboxData<TId>`、`IOutboxMapper<TAggregate,TData>`、`NotMapped` 欄位
- **Prompt**：`.ai/prompts/outbox-sub-agent-prompt.md`

### Frontend Sub-agents

#### 19. Frontend Component Generation Agent
- **Prompt**：`.ai/prompts/frontend-component-generation-prompt.md`

#### 20. Frontend API Integration Agent
- **Prompt**：`.ai/prompts/frontend-api-integration-prompt.md`

## 📋 標準工作流程

1. 讀 spec → 解析需求
2. 依元件類型選擇 sub-agent
3. 生成 production code → 生成 tests
4. Code review → 修正
5. Spec compliance（100% gate）

## 💻 實際執行範例（簡版）

### Command Use Case
- Prompt: `.ai/prompts/command-sub-agent-prompt.md`
- 輸入：spec + `project-config.yaml`
- 輸出：Handler + Domain Events + Repository Save

### Query Use Case
- Prompt: `.ai/prompts/query-sub-agent-prompt.md`
- 輸出：Projection + DTO + Mapper

### Controller
- Prompt: `.ai/prompts/controller-code-generation-prompt.md`

### Reactor
- Prompt: `.ai/prompts/reactor-sub-agent-prompt.md`

### Reconciler
- Prompt: `.ai/prompts/reconciler-sub-agent-prompt.md`

### Outbox Pattern
- Prompt: `.ai/prompts/outbox-sub-agent-prompt.md`

## 🔧 使用指南（對使用者）

```
"請使用 command-sub-agent workflow 實作 create-product use case"
"請使用 query-sub-agent workflow 實作 get-product use case"
"請使用 reactor-sub-agent workflow 實作 notify-sprint-to-select-backlog-item"
"請使用 reconciler-sub-agent workflow 實作定期校正"
"請使用 outbox-sub-agent workflow 為 Product 實作 Outbox Pattern"
```

## 🔧 對 Main Agent 的指引（判斷規則）

**Command 特徵**：Create/Update/Delete/Select/Define + 修改狀態 + 產生事件
**Query 特徵**：Get/List/Search + Projection + 無副作用
**Reactor 特徵**：跨聚合事件處理 + MessageBus
**Reconciler 特徵**：Scheduler-driven + `reconcile()` + idempotent

## 📊 效益評估（參考值）

| 指標 | 傳統方式 | Sub-agent 方式 |
|------|---------|---------------|
| 規範違規率 | 30-40% | 5-10% |
| 首次編譯成功率 | 60% | 90% |
| 測試通過率 | 50% | 85% |

## 🔴 重要：Framework API Integration 指南

所有 Infrastructure 相關 sub-agent 必須遵守：
- `.dev/guides/FRAMEWORK-API-INTEGRATION-GUIDE.md`
- OutboxMapper 必須符合內部 adapter 規範
- EF Core 註冊與 profile 隔離

## 🚀 進階使用

### 平行執行
可同時產生多個 use case（確保 context 隔離）。

### 條件執行
Code Review 有 MUST FIX 時必須先修正再進行後續步驟。

## 📝 維護指南

1. 更新 prompt → 同步更新 `DOTNET-COMMON-PITFALLS.md`
2. 更新規範 → 同步更新 `CODE-REVIEW-CHECKLIST.md`
3. 監控效果 → 追蹤規範遵守率與測試通過率

## 🔗 相關文件

- `.ai/CODE-REVIEW-INDEX.md`
- `.ai/prompts/`
- `.dev/standards/`
- `.dev/guides/`

## 📌 快速參考

```
Task: Generate [command-name] use case
Prompt: .ai/prompts/command-sub-agent-prompt.md

Task: Generate tests for [use-case-name]
Prompt: .ai/prompts/usecase-test-generation-prompt.md

Task: Review [use-case-name] implementation
Prompt: .ai/prompts/code-review-prompt.md
```
