# Portable AI Asset Taxonomy

## Goal

為後續 canonical schema 定義統一的 asset taxonomy，避免把 skill、command、prompt fragment、guide、script 混為同一類。

## Primary Asset Types

### 1. `skill`

用途：

- 定義一個高層工作能力與其執行邊界

典型內容：

- purpose
- triggers
- constraints
- input/output contract
- references

目前對應：

- `ddd-ca-hex-architect`
- `code-reviewer`
- `bdd-gwt-test-designer`
- `staged-refactor-implementer`
- `tactical-refactor-implementer`
- `spec-compliance-validator`

### 2. `command`

用途：

- 定義一個可被 agent CLI / prompt interface 直接呼叫的命令型工作單元

典型內容：

- invocation intent
- required inputs
- output expectation
- linked prompt package

目前候選：

- `aggregate-sub-agent`
- `command-sub-agent`
- `query-sub-agent`
- `reactor-sub-agent`
- `frontend-sub-agent`
- `mutation-testing-sub-agent`
- `outbox-sub-agent`
- `profile-config-sub-agent`

### 3. `prompt-package`

用途：

- 封裝一組可重用 prompt 內容，用於 generation、review、validation、testing

典型內容：

- base prompt
- supporting rules
- output expectations
- example links

目前候選：

- `aggregate-code-review`
- `controller-code-generation`
- `controller-test-generation`
- `reactor-code-review`
- `usecase-test-generation`

### 4. `shared-rule`

用途：

- 提供可被多 skill / command / prompt-package 重用的共享規則

目前候選：

- `architecture-config`
- `aspnet-core-conventions`
- `common-rules`
- `domain-rules`
- `dto-conventions`
- `testing-strategy`
- `PROMPT-PORTABILITY-RULES`

### 5. `example`

用途：

- 提供範例片段，供 skill / command / prompt-package 參照

目前候選：

- `dto-structure-example`
- `nsubstitute-example`
- `wolverine-efcore-outbox-example`
- `xunit-bddfy-example`

### 6. `script`

用途：

- 提供可執行的驗證、生成、檢查或同步工具

目前候選：

- `code-review.sh`
- `check-all.sh`
- `check-prompt-portability.sh`
- `generate-check-scripts-from-md.sh`

## Secondary Classification Axes

### By Portability

- `portable`
  - 可跨 agent、跨 repo 重用
- `repo-portable`
  - 適用於本 repo 的多 agent 使用，但帶有本 repo 結構假設
- `wrapper-specific`
  - 只服務某個 agent runtime

### By Audience

- `agent-facing`
- `human-facing`
- `mixed`

### By Lifecycle

- `canonical`
- `wrapper`
- `generated`
- `historical`

## Taxonomy Rules

- `skill` 不等於 human guide
- `command` 不等於 prompt fragment
- `shared-rule` 不應被某個 wrapper 私有化
- `generated` 內容不可成為單一真相
- `wrapper-specific` 內容應儘量薄

## Mapping Guidance

### Current Repo Mapping

- `.ai/`
  - 未來應收納 `skill spec`、`command spec`、`prompt-package`、`shared-rule`、`example`、`script`
- `.claude/skills/`
  - 應收納 `wrapper-specific skill runtime definitions`
- `.dev/guides/ai-collaboration-guides/`
  - 應收納 `human-facing guides`

## Schema Implication

Stage 2 的 canonical schema 至少要能區分：

- `asset_type`
- `portability`
- `audience`
- `wrapper_targets`
- `source_of_truth`
