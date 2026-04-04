# Session Handoff 2026-03-29 Stage G Progress

## Purpose

這份 handoff 記錄 Stage G 在目前 session 已完成的規劃與文件清理進度，供新的 chat session 或其他 AI agent 直接接手。

## Latest Commits

- `2f54bdb` `Plan command-to-skill convergence stage`
- `b7fa5bf` `Checkpoint stage g partial reference migration`
- `91ca60d` `Finish stage g phase 1 reference neutralization`
- `31b63db` `Add skill wrappers for command query reactor`
- `55a9d8a` `Deprecate legacy command specs`
- `f7f6f59` `Clean active docs for skill-first sub-agents`
- `1149528` `Finalize claude wrapper strategy for use-case skills`
- `e61282e` `Mark remaining active old references as legacy`
- `7bf33ff` `Correct sub-agent taxonomy for command query reactor`
- `c402d62` `Convert remaining sub-agent prompts to canonical assets`

## Current Direction

- repo 已進入 `portable canonical assets + repo-local wrappers` 模型
- top-level runtime capabilities 以 `skills` 為主
- delegated worker-role prompts 應建模為 `.ai/assets/sub-agent-role-prompts/`
- `.ai/assets/commands/` 與相關 legacy prompt package 已自 repo 移除，wrapper 只應指向 canonical sub-agent assets
- `apply_patch` 在此 runtime 對 `.codex*` 前綴路徑失效；`.codex/...` 檔案需用 shell-based edits
- `command/query/reactor/aggregate/frontend/mutation-testing/outbox/profile-config` 已收斂為 canonical sub-agent role prompt taxonomy，不再視為 top-level skills
- `code review` 與 `test generation` 現在也採雙層模型：top-level skill + delegated sub-agent role

## Completed In This Session

### 1. Canonical Reference Neutralization

- `bdd-gwt-test-designer`
- `staged-refactor-implementer`
- `tactical-refactor-implementer`

上述三個 skills 的 references 已搬到 `.ai/assets/skills/<skill-id>/references/`，canonical skill specs 與 Codex wrappers 也已改指向 canonical paths。

### 2. Command / Query / Reactor Sub-Agent Canonicalization

已新增：

- `.ai/assets/sub-agent-role-prompts/command-sub-agent/`
- `.ai/assets/sub-agent-role-prompts/query-sub-agent/`
- `.ai/assets/sub-agent-role-prompts/reactor-sub-agent/`

原先誤建的 `command-use-case-implementer` / `query-use-case-implementer` / `reactor-implementer` top-level skills 已完成回退。

### 3. Legacy Command Layer Removed

- `.ai/assets/commands/README.MD`

原先 legacy command-spec 與 prompt-package 已於後續清理階段移除。

### 4. Active Docs Updated

已更新活躍文件，改以 canonical sub-agent-role-prompt taxonomy 描述 delegated sub-agents：

- `.ai/SUB-AGENT-SYSTEM.MD`
- `.ai/DIRECTORY-RULES.MD`

- `.ai/assets/skills/ddd-ca-hex-architect/references/source-map.md`
- `.ai/assets/skills/staged-refactor-implementer/references/execution-playbook.md`
- `.dev/workflows/2026-03-portable-ai-asset-architecture/prompt-retention-checklist.md`
- `.dev/workflows/2026-03-portable-ai-asset-architecture/tasks/stage-g-command-to-skill-convergence.json`
- `.claude/skills/README.md`
- `.claude/skills/staged-refactor-implementer/references/execution-playbook.md`
- `.gemini/commands/command-sub-agent.md`
- `.gemini/commands/query-sub-agent.md`
- `.gemini/commands/reactor-sub-agent.md`
- `.github/prompts/command-sub-agent.md`
- `.github/prompts/query-sub-agent.md`
- `.github/prompts/reactor-sub-agent.md`

### 5. Active Validation Script Updated

已更新活躍 validation script 與 handoff，避免再把已移除的 legacy prompt / command layer 當成檢查或相容層目標：

- `.ai/scripts/check-coding-standards.sh`

### 6. Remaining Sub-Agent Prompt Families Converted

已新增：

- `.ai/assets/sub-agent-role-prompts/aggregate-sub-agent/`
- `.ai/assets/sub-agent-role-prompts/frontend-sub-agent/`
- `.ai/assets/sub-agent-role-prompts/mutation-testing-sub-agent/`
- `.ai/assets/sub-agent-role-prompts/outbox-sub-agent/`
- `.ai/assets/sub-agent-role-prompts/profile-config-sub-agent/`

並已更新活躍文件指向新的 canonical assets：

- `.ai/SUB-AGENT-SYSTEM.MD`
- `.ai/assets/skills/ddd-ca-hex-architect/references/source-map.md`
- `.ai/assets/skills/staged-refactor-implementer/references/execution-playbook.md`
- `.claude/skills/staged-refactor-implementer/references/execution-playbook.md`
- `.ai/assets/sub-agent-role-prompts/frontend-sub-agent/references/api-integration-guidance.md`
- `.ai/assets/sub-agent-role-prompts/frontend-sub-agent/references/component-generation-guidance.md`
- `.dev/guides/design-guides/FRAMEWORK-API-INTEGRATION-GUIDE.md`
- `.dev/guides/learning-guides/NEW-PROJECT-GUIDE.md`

### 7. Skill / Sub-Agent Boundary Accepted

已新增正式決策：

- `.dev/adr/ADR-050-skill-and-sub-agent-boundary.md`

並新增 delegated review / test-generation canonical assets：

- `.ai/assets/sub-agent-role-prompts/code-review-sub-agent/`
- `.ai/assets/sub-agent-role-prompts/aggregate-code-review-sub-agent/`
- `.ai/assets/sub-agent-role-prompts/usecase-test-sub-agent/`
- `.ai/assets/sub-agent-role-prompts/aggregate-test-sub-agent/`
- `.ai/assets/sub-agent-role-prompts/reactor-test-sub-agent/`

其中的設計原則是：

- `bdd-gwt-test-designer` 保持 top-level test design skill
- `code-reviewer` 保持 top-level review skill
- delegated test implementation / delegated review 收斂為 sub-agent role prompts
- `controller-test-generation-prompt.md` 已比照其他 test generation 資產收斂為 canonical sub-agent role prompt
- `contract-test-generation-prompt.md` 目前保留為 supporting material
- `controller-code-review-prompt.md` 與 `reactor-code-review-prompt.md` 已收斂為 canonical delegated review sub-agent assets

### 8. Shared / Explanatory Materials Locked

下列文件已定稿為 shared / supporting materials，保留在 `.ai/assets/`：

- `PROMPT-PORTABILITY-RULES.md`
- `spec-compliance-rules.md`
- `test-validation-steps.md`
- `testing-standards-prompt.md`
- `code-review-checklist.md`
- `.ai/assets/shared/*`

它們不再作為待升格 skill 或 sub-agent 的候選，而是作為 canonical supporting materials 被其他 skill / sub-agent 引用。

## Current Open Decisions

### 1. Use-Case Sub-Agent Canonical Source

目前決議已定稿：

- use-case sub-agents 的唯一 canonical source 定義在 `.ai/assets/sub-agent-role-prompts/`
- 它們不應被建模成 top-level skills
- Gemini / GitHub 相關 wrapper 目前直接指向 corrected canonical sub-agent source，不再透過 legacy command-spec layer

### 2. Remaining Command-Style Prompt Migration

已完成主要 sub-agent families 的 canonicalization；剩餘待判斷的重點已轉為「哪些 prompt 保留為 explanatory / shared / review / test-generation materials」。

### 3. Judgment Queue

已定稿：

- `validation-command-templates.md` 保留為 shared validation/report template material
- `code-review-prompt.md` 收斂為 `sub-agent-role-prompts/code-review-sub-agent`
- `aggregate-code-review-prompt.md` 收斂為 `sub-agent-role-prompts/aggregate-code-review-sub-agent`
- `aggregate-test-generation-prompt.md` 收斂為 `sub-agent-role-prompts/aggregate-test-sub-agent`
- `contract-test-generation-prompt.md` 保留為 DBC 專用 supporting material
- `controller-test-generation-prompt.md` 收斂為 `sub-agent-role-prompts/controller-test-sub-agent`
- `reactor-test-generation-prompt.md` 收斂為 `sub-agent-role-prompts/reactor-test-sub-agent`
- `usecase-test-generation-prompt.md` 收斂為 `sub-agent-role-prompts/usecase-test-sub-agent`
- `controller-code-review-prompt.md` 收斂為 `sub-agent-role-prompts/controller-code-review-sub-agent`
- `reactor-code-review-prompt.md` 收斂為 `sub-agent-role-prompts/reactor-code-review-sub-agent`

目前 judgment queue 已清空；剩餘的是 documentation cleanup 與歷史文件清理。

### 4. Legacy Layer Cleanup Follow-Up

已完成：

- `.ai/assets/commands/` 已自 repo 移除
- `.ai/assets/shared/prompt-packages/dotnet-usecase-sub-agents/package.yaml` 已自 repo 移除
- `.ai/scripts/check-coding-standards.sh` 已停止檢查已刪除的 legacy sub-agent prompts

後續重點：

- 清理仍存在於歷史文件、inventory 與 stage notes 的舊引用

### 5. Mistaken Top-Level Skill Rollback

已完成：

- 已移除 `.ai/assets/skills/command-use-case-implementer/`
- 已移除 `.ai/assets/skills/query-use-case-implementer/`
- 已移除 `.ai/assets/skills/reactor-implementer/`
- 已移除對應 `.codex/skills/` wrappers
- 已移除對應 `.claude/skills/` wrappers
- 已更新 `.codex/skills/README.md` 與 `.claude/skills/README.md`

## Recommended Resume Order

1. Read:
   - `.dev/workflows/2026-03-portable-ai-asset-architecture/workflow-plan.md`
   - `.dev/workflows/2026-03-portable-ai-asset-architecture/stage-g-command-to-skill-convergence.md`
   - `.dev/workflows/2026-03-portable-ai-asset-architecture/prompt-retention-checklist.md`
   - `.dev/workflows/2026-03-portable-ai-asset-architecture/tasks/stage-g-command-to-skill-convergence.json`
2. Check `git status --short`
3. Verify current stage artifacts and current wrappers stay aligned with the canonical sub-agent model
4. Clean remaining historical docs, ADRs, inventories, and scripts that still mention the old prompt-first model
5. Prioritize stage notes and handoff artifacts that could mislead a new session about the removed legacy layer




