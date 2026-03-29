# Stage 1 Inventory And Taxonomy

> Historical snapshot: 本文件反映 Stage 1 當時的原始盤點結果，包含後來已被移除或重新分類的 prompt / command 資產。請不要將其中的舊 taxonomy 視為目前 canonical model。

本文件整理目前 repo 內 AI assets 的現況盤點，作為後續 canonical schema 與 wrapper strategy 的基礎。

## Inventory Summary

### Repo-Local Skills

目前 skill 本體位於 `.claude/skills/`：

- `bdd-gwt-test-designer`
- `code-reviewer`
- `ddd-ca-hex-architect`
- `spec-compliance-validator`
- `staged-refactor-implementer`
- `tactical-refactor-implementer`

### Prompt Assets

目前 prompts 主要位於 `.ai/assets/`，可分成下列類別：

- command / sub-agent prompts
  - `command-sub-agent-prompt.md`
  - `query-sub-agent-prompt.md`
  - `reactor-sub-agent-prompt.md`
  - `aggregate-sub-agent-prompt.md`
  - `frontend-sub-agent-prompt.md`
  - `mutation-testing-sub-agent-prompt.md`
  - `outbox-sub-agent-prompt.md`
  - `profile-config-sub-agent-prompt.md`
- generation prompts
  - `controller-code-generation-prompt.md`
  - `frontend-component-generation-prompt.md`
  - `frontend-api-integration-prompt.md`
- review prompts
  - `code-review-prompt.md`
  - `aggregate-code-review-prompt.md`
  - `controller-code-review-prompt.md`
  - `reactor-code-review-prompt.md`
- test design / generation prompts
  - `aggregate-test-generation-prompt.md`
  - `controller-test-generation-prompt.md`
  - `contract-test-generation-prompt.md`
  - `reactor-test-generation-prompt.md`
  - `usecase-test-generation-prompt.md`
- validation / rule prompts
  - `code-review-checklist.md`
  - `spec-compliance-rules.md`
  - `test-validation-steps.md`
  - `testing-standards-prompt.md`
  - `validation-command-templates.md`
  - `PROMPT-PORTABILITY-RULES.md`

### Shared Prompt Fragments

目前 shared fragments 位於 `.ai/assets/shared/`：

- `architecture-config.md`
- `aspnet-core-conventions.md`
- `common-rules.md`
- `domain-rules.md`
- `dto-conventions.md`
- `fresh-project-init.md`
- `testing-strategy.md`

### Prompt Examples

目前 examples 位於 `.dev/standards/examples/`：

- `dto-structure-example.md`
- `nsubstitute-example.md`
- `wolverine-efcore-outbox-example.md`
- `xunit-bddfy-example.md`

### Script Assets

目前 scripts 位於 `.ai/scripts/`，可分成：

- review / validation scripts
  - `code-review.sh`
  - `check-all.sh`
  - `check-spec-compliance.sh`
  - `check-prompt-portability.sh`
- rule-derived checks
  - `check-aggregate-compliance.sh`
  - `check-controller-compliance.sh`
  - `check-mapper-compliance.sh`
  - `check-projection-compliance.sh`
  - `check-repository-compliance.sh`
  - `check-test-compliance.sh`
  - `check-usecase-compliance.sh`
- framework / stack checks
  - `check-coding-standards.sh`
  - `check-framework-api-compliance.sh`
  - `check-mutation-coverage.sh`
  - `validate-dual-profile-config.sh`
- generated scripts
  - `.ai/scripts/generated/check-*.sh`
- script support files
  - `README.md`
  - `MD-SCRIPT-GENERATION-GUIDE.md`
  - `parse-md-rules.py`
  - `generate-check-scripts-from-md.sh`

## Known Agent Wrapper Interfaces

### Existing

- Claude:
  - `.claude/skills/`
- Gemini:
  - `.gemini/settings.json`

### Expected By Current Repo Docs

- Codex:
  - `.codex/prompts/`
- Gemini:
  - `.gemini/commands/`
- GitHub Copilot:
  - `.github/prompts/`
  - `.github/copilot-instructions.md`

這些位置應視為 repo-level wrapper interfaces，而不是 canonical source。

## Taxonomy

### Asset Types

建議將 AI assets 分成下列中立類型：

- `skill-spec`
  - 一個可跨 agent 描述的 skill 定義
- `command-spec`
  - 一個可跨 agent 描述的 command / slash command / workflow command
- `prompt-package`
  - 一組 prompts、shared fragments、examples 的組合
- `shared-rule`
  - 通用規則、contracts、templates
- `script-asset`
  - validation / generation / export / sync scripts
- `wrapper`
  - agent-specific runtime-facing definition
- `guide`
  - human-facing 使用說明

### Canonical vs Wrapper vs Guide

#### Canonical Candidates

下列內容適合作為 canonical source：

- skill purpose / overview
- triggers
- workflow steps
- boundaries / constraints
- input / output contract
- references / playbooks
- shared prompt fragments
- examples
- command intent

#### Wrapper-Specific Content

下列內容應保留在 wrapper 層：

- agent runtime metadata
- agent-specific trigger syntax
- agent-specific config file shape
- thin pointer files bridging runtime to canonical source

#### Human-Facing Guide Content

下列內容應保留在 `.dev/guides/ai-collaboration-guides/`：

- 使用方式
- prompt templates
- workflow explanations
- when-to-use guidance
- cross-skill / cross-command pairing guides

## Stage 1 Findings

### Finding 1

`.claude/skills/` 目前是 canonical content 與 wrapper metadata 混合狀態。

### Finding 2

`.ai/assets/` 目前同時承擔：

- command family
- prompt package
- validation rules
- examples

因此後續需要更明確的 canonical schema 與子類別。

### Finding 3

repo 內已存在或被 README 明示的 wrapper interface 並不一致：

- Claude 偏 skill-oriented
- Codex 偏 prompt-oriented
- Gemini 偏 commands-oriented
- Copilot 偏 prompt/instructions-oriented

因此 wrapper strategy 必須接受「不同 agent 的 wrapper 粒度不同」。

### Finding 4

若要避免多份真相，下一階段應優先定義：

- `skill-spec` schema
- `command-spec` schema
- `prompt-package` schema

而不是先建立多個 agent-specific 目錄。


