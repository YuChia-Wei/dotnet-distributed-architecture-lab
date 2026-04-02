# Portable AI Asset Inventory

> Historical snapshot: 本文件記錄的是重構初期的資產盤點，部分內容已被後續的 canonical skill / sub-agent-role 模型取代。使用目前狀態時，應以 `refactor-plan.md`、`prompt-retention-checklist.md`、`SKILL-AND-SUB-AGENT-TAXONOMY-GUIDE.md` 與最新 task / handoff 記錄為準。

## Purpose

盤點目前 repo 內與 AI collaboration 相關的可重用資產，作為 portable canonical source 設計的基礎。

## Current Asset Zones

| Zone | Current Role | Notes |
|------|--------------|-------|
| `.ai/` | agent-facing reusable prompts / rules / scripts | 最接近 portable source，但仍缺少明確 schema |
| `.claude/skills/` | repo-local skill wrappers / runtime-facing definitions | 已有 skill 結構，但偏 agent-specific |
| `.dev/guides/ai-collaboration-guides/` | human-facing guides | 已有完整 guide / workflow / contract 入口 |
| `.dev/refactor-workflows/` | workflow artifacts | 保存規劃與執行中的 plan / task / review |

## Repo-Local Skills Inventory

### `bdd-gwt-test-designer`

- Files:
  - `SKILL.md`
  - `references/output-contract.md`
  - `references/scenario-design-playbook.md`
  - `references/scope-rules.md`
- Likely canonical candidates:
  - scenario design rules
  - output contract
  - scope rules
- Likely wrapper-specific content:
  - `SKILL.md` frontmatter / runtime phrasing

### `code-reviewer`

- Files:
  - `SKILL.md`
  - `CHECKLIST-REFERENCE.MD`
- Likely canonical candidates:
  - review rules
  - findings format
  - scoring expectations
- Likely wrapper-specific content:
  - `SKILL.md` trigger / runtime instructions

### `ddd-ca-hex-architect`

- Files:
  - `SKILL.md`
  - `agents/openai.yaml`
  - `references/architecture-playbook.md`
  - `references/design-deliverables.md`
  - `references/prompt-templates.md`
  - `references/source-map.md`
- Likely canonical candidates:
  - architecture playbook
  - design deliverables
  - source map
  - prompt template intent
- Likely wrapper-specific content:
  - `SKILL.md`
  - `agents/openai.yaml`
  - thin pointer file under `references/prompt-templates.md`

### `spec-compliance-validator`

- Files:
  - `SKILL.md`
- Likely canonical candidates:
  - validation behavior
- Likely wrapper-specific content:
  - current skill packaging

### `staged-refactor-implementer`

- Files:
  - `SKILL.md`
  - `agents/openai.yaml`
  - `references/execution-playbook.md`
  - `references/input-contract.md`
  - `references/skill-boundaries.md`
- Likely canonical candidates:
  - execution playbook
  - input contract
  - boundaries
- Likely wrapper-specific content:
  - `SKILL.md`
  - `agents/openai.yaml`

### `tactical-refactor-implementer`

- Files:
  - `SKILL.md`
  - `agents/openai.yaml`
  - `references/allowed-operations.md`
  - `references/execution-rules.md`
  - `references/skill-boundaries.md`
- Likely canonical candidates:
  - allowed operations
  - execution rules
  - boundaries
- Likely wrapper-specific content:
  - `SKILL.md`
  - `agents/openai.yaml`

## Prompt Inventory

### Command / Sub-Agent Prompt Families

- `aggregate-sub-agent-prompt.md`
- `command-sub-agent-prompt.md`
- `query-sub-agent-prompt.md`
- `reactor-sub-agent-prompt.md`
- `frontend-sub-agent-prompt.md`
- `mutation-testing-sub-agent-prompt.md`
- `outbox-sub-agent-prompt.md`
- `profile-config-sub-agent-prompt.md`

These look like strong candidates for `command` or `workflow` canonical specs.

### Review / Validation Prompt Families

- `aggregate-code-review-prompt.md`
- `code-review-prompt.md`
- `controller-code-review-prompt.md`
- `reactor-code-review-prompt.md`
- `code-review-checklist.md`
- `spec-compliance-rules.md`
- `test-validation-steps.md`
- `testing-standards-prompt.md`
- `validation-command-templates.md`

These look like reusable review or validation prompt packages.

### Generation / Test Design Prompt Families

- `aggregate-test-generation-prompt.md`
- `contract-test-generation-prompt.md`
- `controller-code-generation-prompt.md`
- `controller-test-generation-prompt.md`
- `frontend-api-integration-prompt.md`
- `frontend-component-generation-prompt.md`
- `reactor-test-generation-prompt.md`
- `usecase-test-generation-prompt.md`

These look like command family content or prompt packages rather than standalone skills.

### Shared Prompt Fragments

- `shared/architecture-config.md`
- `shared/aspnet-core-conventions.md`
- `shared/common-rules.md`
- `shared/domain-rules.md`
- `shared/dto-conventions.md`
- `shared/fresh-project-init.md`
- `shared/testing-strategy.md`

These are already close to canonical reusable fragments.

### Examples

- `examples/dto-structure-example.md`
- `examples/nsubstitute-example.md`
- `examples/wolverine-efcore-outbox-example.md`
- `examples/xunit-bddfy-example.md`

These should likely remain as canonical examples, linked by future specs.

### Rules / Portability Files

- `PROMPT-PORTABILITY-RULES.md`

This is already canonical policy-level content.

## Script Inventory

### Review / Quality Scripts

- `code-review.sh`
- `check-all.sh`
- `check-coding-standards.sh`
- `check-prompt-portability.sh`

### Pattern-Specific Check Scripts

- `check-aggregate-compliance.sh`
- `check-archive-compliance.sh`
- `check-controller-compliance.sh`
- `check-domain-events-compliance.sh`
- `check-framework-api-compliance.sh`
- `check-jpa-projection-config.sh`
- `check-mapper-compliance.sh`
- `check-projection-compliance.sh`
- `check-repository-compliance.sh`
- `check-spec-compliance.sh`
- `check-test-compliance.sh`
- `check-usecase-compliance.sh`

### Environment / Config Scripts

- `check-data-class-annotations.sh`
- `check-spring-config.sh`
- `check-test-spring-di.sh`
- `test-profile-startup.sh`
- `validate-dual-profile-config.sh`
- `check-dockerfile-csproj-copy-sync.ps1`

### Generation / Parsing Scripts

- `generate-check-scripts-from-md.sh`
- `parse-md-rules.py`
- `generated/check-*.sh`
- `MD-SCRIPT-GENERATION-GUIDE.md`

## Agent-Neutral Vs Wrapper-Tied Assessment

### Already Agent-Neutral Or Close

- `.ai/assets/shared/*`
- `.dev/standards/examples/reference/*`
- `.ai/assets/shared/PROMPT-PORTABILITY-RULES.md`
- most `.ai/scripts/*`
- most skill `references/*`

### Currently Wrapper-Tied

- `.claude/skills/*/SKILL.md`
- `.claude/skills/*/agents/openai.yaml`
- `.claude/skills/*/CHECKLIST-REFERENCE.MD` when its wording assumes current runtime usage

### Mixed / Needs Separation

- `.ai/assets/*-sub-agent-prompt.md`
  - content is portable in intent, but currently organized as flat prompt files rather than canonical command specs
- `.ai/assets/*-code-review-prompt.md`
  - likely portable, but missing explicit metadata / taxonomy

## Suggested Taxonomy Fields

For any future canonical asset spec, the minimum useful fields appear to be:

- `id`
- `asset_type`
  - `skill | command | prompt-package | shared-rule | example | script`
- `purpose`
- `primary_inputs`
- `expected_outputs`
- `triggers`
- `constraints`
- `references`
- `examples`
- `wrapper_targets`
  - `claude | codex | gemini | copilot`
- `human_guide`
- `status`



