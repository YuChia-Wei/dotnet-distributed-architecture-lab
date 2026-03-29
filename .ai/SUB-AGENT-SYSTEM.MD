# Sub-agent System Architecture (.NET)

本文件定義 .NET Sub-agent 系統架構，適用於 WolverineFx + EF Core + xUnit + BDDfy。

## Current Direction

- `command-sub-agent`、`query-sub-agent`、`reactor-sub-agent` 這三類 use case / consistency sub-agents 已改收斂為 sub-agent role prompts
- 其 canonical source 應以 `.ai/assets/sub-agent-role-prompts/` 下的 `sub-agent.yaml` 與 references 為準，而不再以單一 prompt 檔作為唯一真相
- 它們不應被視為 top-level skills
- `bdd-gwt-test-designer` 與 `code-reviewer` 保持 top-level skills；test generation 與 delegated review 應優先建模為 sub-agent role prompts
- 若未來需要 delegated runtime wrapper，應在專門的 sub-agent wrapper strategy 中處理
- 舊 prompt-first sub-agent assets 與 `.ai/assets/commands/*` 已自活躍層移除，不應再作為主入口或相容層依賴

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
- **Canonical Sub-Agent Asset**：`.ai/assets/sub-agent-role-prompts/command-sub-agent/sub-agent.yaml`

#### 1b. Query Code Generation Agent
- **職責**：產生 Query use case 的 production code
- **專注領域**：Projection 設計、DTO mapping、Read model
- **Canonical Sub-Agent Asset**：`.ai/assets/sub-agent-role-prompts/query-sub-agent/sub-agent.yaml`

#### 2. Test Generation Agent
- **職責**：產生測試程式碼
- **專注領域**：xUnit + BDDfy（Gherkin 風格命名）、NSubstitute
- **限制**：禁止 BaseTestClass
- **Canonical Sub-Agent Asset**：`.ai/assets/sub-agent-role-prompts/usecase-test-sub-agent/sub-agent.yaml`
- **Upstream Skill**：`.ai/assets/skills/bdd-gwt-test-designer/skill.yaml`

#### 3. Code Review Agent
- **職責**：審查程式碼品質與規範遵守
- **Canonical Sub-Agent Asset**：`.ai/assets/sub-agent-role-prompts/code-review-sub-agent/sub-agent.yaml`
- **Top-Level Review Skill**：`.ai/assets/skills/code-reviewer/skill.yaml`

### Testing Enhancement Sub-agents

#### 4. Contract Test Generation Agent
- **職責**：產生 Aggregate Contract Tests（DBC preconditions）
- **目前定位**：僅保留為 Design by Contract 專用的 supporting guidance，不建立獨立 canonical sub-agent
- **暫行規則**：使用純 xUnit；每個 command method 對應獨立 contract test class；以 `Assert.Throws<PreconditionViolationException>` 驗證 preconditions
- **預設輸出位置**：`src/tests/Domain/<Aggregate>/Contracts/<Aggregate>ContractTests.cs`
- **狀態**：待未來 Design by Contract 規範成熟後，再評估是否升格為 canonical sub-agent

#### 5. Mutation Testing Enhancement Agent
- **職責**：Stryker.NET + uContract + assertion-free tests
- **Canonical Sub-Agent Asset**：`.ai/assets/sub-agent-role-prompts/mutation-testing-sub-agent/sub-agent.yaml`
- **腳本**：`.ai/scripts/check-mutation-coverage.sh`

### Controller Sub-agents

#### 6. Controller Code Generation Agent
- **Prompt**：`.ai/assets/sub-agent-role-prompts/controller-sub-agent/references/implementation-guidance.md`

#### 7. Controller Test Generation Agent
- **Canonical Sub-Agent Asset**：`.ai/assets/sub-agent-role-prompts/controller-test-sub-agent/sub-agent.yaml`
- **Upstream Skill**：`.ai/assets/skills/bdd-gwt-test-designer/skill.yaml`

#### 8. Controller Code Review Agent
- **Canonical Sub-Agent Asset**：`.ai/assets/sub-agent-role-prompts/controller-code-review-sub-agent/sub-agent.yaml`
- **Top-Level Review Skill**：`.ai/assets/skills/code-reviewer/skill.yaml`

### Aggregate Sub-agents

#### 9. Aggregate Code Generation Agent
- **Canonical Sub-Agent Asset**：`.ai/assets/sub-agent-role-prompts/aggregate-sub-agent/sub-agent.yaml`

#### 10. Aggregate Test Generation Agent
- **Canonical Sub-Agent Asset**：`.ai/assets/sub-agent-role-prompts/aggregate-test-sub-agent/sub-agent.yaml`
- **Upstream Skill**：`.ai/assets/skills/bdd-gwt-test-designer/skill.yaml`

#### 11. Aggregate Code Review Agent
- **Canonical Sub-Agent Asset**：`.ai/assets/sub-agent-role-prompts/aggregate-code-review-sub-agent/sub-agent.yaml`
- **Top-Level Review Skill**：`.ai/assets/skills/code-reviewer/skill.yaml`

### Reactor Sub-agents

#### 12. Reactor Code Generation Agent
- **職責**：跨聚合事件處理 / Read model projection / MQ integration
- **Canonical Sub-Agent Asset**：`.ai/assets/sub-agent-role-prompts/reactor-sub-agent/sub-agent.yaml`

#### 13. Reactor Test Generation Agent
- **Canonical Sub-Agent Asset**：`.ai/assets/sub-agent-role-prompts/reactor-test-sub-agent/sub-agent.yaml`
- **Upstream Skill**：`.ai/assets/skills/bdd-gwt-test-designer/skill.yaml`

#### 14. Reactor Code Review Agent
- **Canonical Sub-Agent Asset**：`.ai/assets/sub-agent-role-prompts/reactor-code-review-sub-agent/sub-agent.yaml`
- **Top-Level Review Skill**：`.ai/assets/skills/code-reviewer/skill.yaml`

### Reconciler Sub-agents

#### 15. Reconciler Code Generation Agent
- **職責**：定期校正跨聚合狀態漂移（Scheduler 驅動）
- **核心要求**：入口 `reconcile()`、idempotent、跨聚合查詢
- **Canonical Asset**：`.ai/assets/sub-agent-role-prompts/reconciler-sub-agent/`（TODO：尚未建立）

### Specification Sub-agents

#### 16. Problem Frame Sub-agent
- **職責**：從 Problem Frame 規格產生完整功能
- **來源**：`.dev/problem-frames/*.yaml`（若未存在，請標記 TODO）
- **要求**：Spec compliance 100% gate
- **Canonical Asset**：`.ai/assets/sub-agent-role-prompts/problem-frame-sub-agent/`（若尚未建立，請標記 TODO）

### Infrastructure Sub-agents

#### 17. Profile Configuration Agent
- **職責**：設定 `test-inmemory` / `test-outbox` profiles
- **重點**：profile 完全隔離、EF Core 註冊分離
- **Canonical Sub-Agent Asset**：`.ai/assets/sub-agent-role-prompts/profile-config-sub-agent/sub-agent.yaml`

#### 18. Outbox Pattern Implementation Agent
- **職責**：OutboxData / OutboxMapper / Repository 配置
- **重點**：`IOutboxData<TId>`、`IOutboxMapper<TAggregate,TData>`、`NotMapped` 欄位
- **Canonical Sub-Agent Asset**：`.ai/assets/sub-agent-role-prompts/outbox-sub-agent/sub-agent.yaml`

### Frontend Sub-agents

#### 19. Frontend Component Generation Agent
- **Prompt**：`.ai/assets/sub-agent-role-prompts/frontend-sub-agent/references/component-generation-guidance.md`

#### 20. Frontend API Integration Agent
- **Canonical Sub-Agent Asset**：`.ai/assets/sub-agent-role-prompts/frontend-sub-agent/sub-agent.yaml`

## 📋 標準工作流程

1. 讀 spec → 解析需求
2. 依元件類型選擇 sub-agent
3. 生成 production code → 生成 tests
4. Code review → 修正
5. Spec compliance（100% gate）

## 📂 Artifact Routing Rule

當 sub-agent 或多 agent 協作需要共享上下文時，應優先使用 `.dev/` 下的正式文件，而不是把狀態散落在 prompt 或臨時筆記中。

### Requirement

- 需求來源優先讀取 `.dev/requirement/`
- 用於 functional / non-functional requirement、限制條件、品質屬性

### Specs

- 功能行為與驗收條件優先讀取 `.dev/specs/`
- 用於 use case、規則、行為流程、驗證基準

### Refactor Workflow Artifacts

- 若任務進入 multi-skill 或 multi-agent handoff，workflow artifact 應放在 `.dev/refactor-workflows/`
- 標準位置：
  - `.dev/refactor-workflows/<workflow-id>/refactor-plan.md`
  - `.dev/refactor-workflows/<workflow-id>/review-report.md`
  - `.dev/refactor-workflows/<workflow-id>/tasks/<task-id>.json`

### 讀寫原則

- architect / reviewer / refactor implementer 類型 agent 可讀取 workflow artifact
- 若任務明確要求更新 stage 狀態或結果，可更新對應 `tasks/<task-id>.json`
- 未被授權更新 artifact 的 sub-agent，預設只讀不寫
- 不要把 workflow artifact 散放到 `.ai/`、`.claude/skills/`、feature 目錄或臨時文件

## 🤝 Refactor Skill Integration Rule

sub-agent 不應自行取代 refactor skills。
當任務涉及重構決策、review、stage execution 或 tactical cleanup 時，應依下列分工與對應關係協作。

### `ddd-ca-hex-architect`

適用於：

- 懷疑需要重畫邊界、重新切 stage、重新決定依賴方向
- extract class / extract interface
- semantic rename
- 任何可能從局部整理升級成結構性改動的任務

與 sub-agent 的關係：

- Command / Query / Reactor / Aggregate 類型 sub-agent 若遇到邊界衝突，應先回到 architect
- architect 輸出的 plan 可供後續 implementer 或相關 sub-agent 讀取

### `code-reviewer`

適用於：

- 對既有實作、既有 stage 結果、既有 generated code 做規則審查
- 區分 architecture-level 與 code-level findings

與 sub-agent 的關係：

- Code Review Agent 可視為與 `code-reviewer` 同類型的審查角色
- delegated code-review sub-agents 應視為 `code-reviewer` 的 worker roles，而不是新的 top-level review skill
- generation sub-agent 不應自稱完成 review；如需正式 findings，應交給 reviewer

### `staged-refactor-implementer`

適用於：

- 已有 architect direction 或 review findings
- 需要在單一 stage 內做 bounded implementation change
- 需要明確維持相容性、限制 scope、更新驗證

與 sub-agent 的關係：

- 若 Command / Query / Reactor / Aggregate 類型 sub-agent 的任務其實是 stage 級重構，應優先由 staged implementer 主導
- 專門的 generation sub-agent 可作為 stage 內的執行幫手，但不應自行擴張 scope

### `tactical-refactor-implementer`

適用於：

- extract method
- safe local rename
- 一個主要目標周圍的小範圍局部整理

與 sub-agent 的關係：

- 一般 generation sub-agent 不應直接宣告自己在做 tactical refactor
- 若只是單一類別內的 extract method 或 local rename，可由 main agent 直接使用 tactical skill
- 若 sub-agent 被要求處理這類小範圍整理，應遵守 tactical 的 dependency radius，不得擴張成新型別引入

## 🧭 Sub-agent 與 Refactor Skill 對照

| 類型 | 預設搭配 | 何時升級 |
| :--- | :--- | :--- |
| Command / Query / Reactor / Aggregate generation | `staged-refactor-implementer` | 需要重畫邊界、extract class/interface、semantic rename 時升級到 `ddd-ca-hex-architect` |
| Test generation | `bdd-gwt-test-designer` + `staged-refactor-implementer` 或 `tactical-refactor-implementer` | 若測試缺口反映架構問題，回到 `code-reviewer` 或 `ddd-ca-hex-architect` |
| Code Review Agent | `code-reviewer` | 若 findings 指向 architecture decision，交回 `ddd-ca-hex-architect` |
| Profile / Outbox / Infrastructure agents | `staged-refactor-implementer` | 若涉及結構重切或命名語意變更，先經 `ddd-ca-hex-architect` |

## ✍ Artifact 更新權限

- `ddd-ca-hex-architect`:
  - 可建立或更新 `refactor-plan.md`
- `code-reviewer`:
  - 可建立或更新 `review-report.md`
- `staged-refactor-implementer` / `tactical-refactor-implementer`:
  - 可建立或更新 `tasks/<task-id>.json`
- 一般 sub-agent:
  - 預設只讀
  - 只有在任務明確要求更新 task 狀態或結果時，才可更新既有 `tasks/<task-id>.json`
  - 不應自行建立新的 `refactor-plan.md` 或 `review-report.md`

## 💻 實際執行範例（簡版）

### Command Use Case
- Canonical Sub-Agent Asset: `.ai/assets/sub-agent-role-prompts/command-sub-agent/sub-agent.yaml`
- 輸入：spec + `project-config.yaml`
- 輸出：Handler + Domain Events + Repository Save

### Query Use Case
- Canonical Sub-Agent Asset: `.ai/assets/sub-agent-role-prompts/query-sub-agent/sub-agent.yaml`
- 輸出：Projection + DTO + Mapper

### Controller
- Canonical Sub-Agent Asset: `.ai/assets/sub-agent-role-prompts/controller-sub-agent/sub-agent.yaml`

### Reactor
- Canonical Sub-Agent Asset: `.ai/assets/sub-agent-role-prompts/reactor-sub-agent/sub-agent.yaml`

### Reconciler
- Canonical Asset: `.ai/assets/sub-agent-role-prompts/reconciler-sub-agent/`（TODO）

### Outbox Pattern
- Canonical Sub-Agent Asset: `.ai/assets/sub-agent-role-prompts/outbox-sub-agent/sub-agent.yaml`

## 🔧 使用指南（對使用者）

```
"請使用 command-sub-agent role prompt 實作 create-product use case"
"請使用 query-sub-agent role prompt 實作 get-product use case"
"請使用 reactor-sub-agent role prompt 實作 notify-sprint-to-select-backlog-item"
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
- `.dev/guides/design-guides/FRAMEWORK-API-INTEGRATION-GUIDE.md`
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
- `.ai/assets/`
- `.dev/requirement/`
- `.dev/specs/`
- `.dev/refactor-workflows/README.MD`
- `.dev/standards/`
- `.dev/guides/`

## 📌 快速參考

```
Task: Generate [command-name] use case
Sub-Agent Asset: .ai/assets/sub-agent-role-prompts/command-sub-agent/sub-agent.yaml

Task: Generate tests for [use-case-name]
Sub-Agent Asset: .ai/assets/sub-agent-role-prompts/usecase-test-sub-agent/sub-agent.yaml

Task: Review [use-case-name] implementation
Sub-Agent Asset: .ai/assets/sub-agent-role-prompts/code-review-sub-agent/sub-agent.yaml
```





