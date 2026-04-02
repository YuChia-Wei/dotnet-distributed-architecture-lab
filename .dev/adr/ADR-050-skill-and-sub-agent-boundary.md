# ADR-050: Skill 與 Sub-Agent 邊界定義

## 狀態
Historical / Superseded

## Current Canonical Source

- `.dev/guides/ai-collaboration-guides/SKILL-AND-SUB-AGENT-TAXONOMY-GUIDE.md`
- `.ai/SUB-AGENT-SYSTEM.MD`
- `.dev/standards/rationale/skill-sub-agent-boundary-rationale.MD`

## Note

本 ADR 的核心價值已轉成可攜式 AI 協作知識。它保留為歷史決策脈絡，不再作為主要入口。

## 日期
2026-03-29

## 背景

在 portable AI asset architecture 重構過程中，出現了兩種不同層級的 AI 資產被混用的問題：

1. 使用者或 main agent 直接啟動的高階能力
2. main agent 在工作流中委派的 bounded worker role

先前曾將部分 `*-sub-agent-prompt.md` 直接轉為 top-level skills，後續確認這會混淆：

- top-level capability
- delegated worker role
- shared prompt material

此混淆會導致：

- taxonomy 不清楚
- wrapper strategy 混亂
- runtime entry 與 canonical source 難以對齊

## 決策

建立明確的雙層模型：

### 1. Skill

`skill` 是使用者或 main agent 可直接啟動的 top-level capability。

特徵：

- 提供高階任務能力
- 可獨立作為 runtime entry
- 面向人類使用者或主 agent
- 可能協調多個 delegated workers

目前代表例：

- `ddd-ca-hex-architect`
- `code-reviewer`
- `spec-compliance-validator`
- `staged-refactor-implementer`
- `tactical-refactor-implementer`
- `bdd-gwt-test-designer`

canonical source 放在：

```text
.ai/assets/skills/<skill-id>/
```

### 2. Sub-Agent Role Prompt

`sub-agent-role-prompt` 是 main agent 在 workflow 中委派給 worker 的角色定義。

特徵：

- 不應預設視為 top-level skill
- 任務邊界穩定、可重複委派
- 輸入輸出明確
- 通常服務於某一類實作、測試、review、整合或基礎設施工作

目前代表例：

- `command-sub-agent`
- `query-sub-agent`
- `reactor-sub-agent`
- `aggregate-sub-agent`
- `outbox-sub-agent`
- `profile-config-sub-agent`
- `frontend-sub-agent`
- `mutation-testing-sub-agent`
- `code-review-sub-agent`
- `aggregate-code-review-sub-agent`
- `usecase-test-sub-agent`
- `aggregate-test-sub-agent`
- `reactor-test-sub-agent`

canonical source 放在：

```text
.ai/assets/sub-agent-role-prompts/<sub-agent-id>/
```

### 3. Shared / Supporting Materials

某些 prompt 或文件不是 top-level skill，也不是完整的 delegated worker role，而是支援性材料。

適用類型：

- checklist
- validation command reference
- report template
- test strategy
- domain/shared rules
- specialized but尚未成熟為獨立 role 的說明文件

代表例：

- `code-review-checklist.md`
- `validation-command-templates.md`
- `contract-test-generation-prompt.md`
- `.ai/assets/shared/*`

## Test Generation 與 Review 的分工

### Test Design vs Test Implementation

`bdd-gwt-test-designer` 保持為 top-level skill，其職責是：

- 解析規格與行為
- 設計 Given-When-Then scenarios
- 提供 assertion plan

它不預設直接實作最終 test code。

因此 test generation 類型資產應優先建模為 delegated sub-agent role，而不是直接升格成新的 top-level skill。

也就是：

- `bdd-gwt-test-designer`：設計
- `usecase-test-sub-agent` / `aggregate-test-sub-agent` / `reactor-test-sub-agent`：實作

### Top-Level Review vs Delegated Review

`code-reviewer` 保持為 top-level skill，其職責是：

- 執行正式 review
- 產出 findings/report
- 區分 architecture-level 與 code-level 問題

而 `code-review-sub-agent` 與 specialized review sub-agent 則用於：

- workflow 內 delegated review
- 特定構件或局部範圍的專門審查

## Wrapper 策略

- top-level skill wrappers 仍由 Claude / Codex 的 repo-local skill wrappers 承接
- sub-agent-role-prompts 不預設要求與 skill 相同的 runtime wrapper 佈局
- 若未來需要 delegated runtime wrappers，應另立 wrapper strategy，不得反向把 sub-agent role 誤建模為 top-level skill

## 結果

此後應遵守：

1. 不要因為某個 prompt 可以被執行，就自動把它升格為 skill
2. 先判斷它是 top-level capability 還是 delegated worker role
3. shared/supporting materials 不強迫 skill 化或 sub-agent 化
4. test generation 與 code review 允許同時存在：
   - top-level skill
   - delegated sub-agent role

## 影響

### 直接影響

- `.ai/assets/skills/` 與 `.ai/assets/sub-agent-role-prompts/` 的界線明確化
- review/test-generation 相關 prompt 需重新依 taxonomy 收斂
- 未來 wrapper strategy 可獨立設計，不再綁死到 skill taxonomy

### 不直接要求

- 不要求每個 skill 都有對應 sub-agent
- 不要求每個 sub-agent 都有獨立 runtime wrapper
- 不要求所有 supporting prompt 立即轉換

## 參考

- `.ai/SUB-AGENT-SYSTEM.MD`
- `.dev/refactor-workflows/2026-03-portable-ai-asset-architecture/sub-agent-asset-strategy-correction.md`
- `.ai/assets/skills/bdd-gwt-test-designer/skill.yaml`
- `.ai/assets/skills/code-reviewer/skill.yaml`

