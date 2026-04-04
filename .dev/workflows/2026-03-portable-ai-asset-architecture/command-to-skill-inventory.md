# Command To Skill Inventory

本文件整理 command / prompt / skill 收斂階段曾盤點的資產，並補上目前已完成的最終結果。

## A. Existing Command Specs

最終結果：

- `.ai/assets/commands/` 已自 repo 移除
- 原先的 `command/query/reactor` command family 已由 `.ai/assets/sub-agent-role-prompts/` 承接
- Gemini / GitHub wrapper 已直接指向 canonical sub-agent assets

歷史盤點快照：

- `command-sub-agent`
- `query-sub-agent`
- `reactor-sub-agent`

共同特徵：

- 皆以 `.ai/assets/*.md` 作為 `prompt_packages`
- 目前 wrapper target 僅剩 `gemini` 與 `copilot`
- 不再有 Codex wrapper 需求

修正後判斷：

- 這三個 command-spec 應視為 legacy compatibility assets
- 不建議再擴充新的 command-spec family
- 對應 canonical source 應放在：
  - `.ai/assets/sub-agent-role-prompts/command-sub-agent/`
  - `.ai/assets/sub-agent-role-prompts/query-sub-agent/`
  - `.ai/assets/sub-agent-role-prompts/reactor-sub-agent/`

## B. Command-Style Prompt Candidates To Convert

下列檔名與用途明顯偏向「可執行型 AI 工作入口」，在當時應優先評估收斂：

- `.ai/assets/aggregate-sub-agent-prompt.md`
- `.ai/assets/command-sub-agent-prompt.md`
- `.ai/assets/query-sub-agent-prompt.md`
- `.ai/assets/reactor-sub-agent-prompt.md`
- `.ai/assets/frontend-sub-agent-prompt.md`
- `.ai/assets/mutation-testing-sub-agent-prompt.md`
- `.ai/assets/outbox-sub-agent-prompt.md`
- `.ai/assets/profile-config-sub-agent-prompt.md`

最終修正結果：

- `command/query/reactor` 不應視為 top-level skill family
- 它們應建模為一組 use case sub-agent role prompt family：
  - `command-sub-agent`
  - `query-sub-agent`
  - `reactor-sub-agent`
- `aggregate/frontend/mutation-testing/outbox/profile-config` 也已依角色收斂到 `sub-agent-role-prompts`
- 原始 `*-sub-agent-prompt.md` 檔案已自 repo 移除

## C. Reusable But Not Necessarily Command-Style

下列檔案更像 reusable generation / review materials，不一定應直接成為 skill：

- `.ai/assets/sub-agent-role-prompts/controller-sub-agent/references/implementation-guidance.md`
- `.ai/assets/sub-agent-role-prompts/controller-code-review-sub-agent/references/review-prompt.md`
- `.ai/assets/sub-agent-role-prompts/controller-test-sub-agent/references/test-generation-guidance.md`
- `.ai/assets/sub-agent-role-prompts/frontend-sub-agent/references/api-integration-guidance.md`
- `.ai/assets/sub-agent-role-prompts/frontend-sub-agent/references/component-generation-guidance.md`
- `.ai/assets/sub-agent-role-prompts/aggregate-code-review-sub-agent/references/review-prompt.md`
- `.ai/assets/sub-agent-role-prompts/reactor-code-review-sub-agent/references/review-prompt.md`
- `.ai/assets/sub-agent-role-prompts/aggregate-test-sub-agent/references/test-generation-guidance.md`
- `.ai/assets/shared/contract-test-generation-guidance.md`
- `.ai/assets/sub-agent-role-prompts/reactor-test-sub-agent/references/test-generation-guidance.md`
- `.ai/assets/sub-agent-role-prompts/usecase-test-sub-agent/references/test-generation-guidance.md`
- `.ai/assets/sub-agent-role-prompts/code-review-sub-agent/references/review-prompt.md`

初步建議：

- 優先視為 skill 的 supporting prompt packages / references 候選
- 不應再以獨立 command 入口方式擴張

## D. Shared / Explanatory Prompts Likely To Keep

下列檔案屬於規則、策略、共用說明，應保留，但後續可調整放置位置：

- `.ai/assets/shared/PROMPT-PORTABILITY-RULES.md`
- `.ai/assets/shared/spec-compliance-rules.md`
- `.ai/assets/shared/test-validation-steps.md`
- `.ai/assets/shared/testing-standards.md`
- `.ai/assets/shared/code-review-checklist.md`
- `.ai/assets/shared/architecture-config.md`
- `.ai/assets/shared/aspnet-core-conventions.md`
- `.ai/assets/shared/common-rules.md`
- `.ai/assets/shared/domain-rules.md`
- `.ai/assets/shared/dto-conventions.md`
- `.ai/assets/shared/fresh-project-init.md`
- `.ai/assets/shared/testing-strategy.md`

初步建議：

- 這批內容應保留
- 長期可逐步收斂到 `.ai/assets/shared/` 或 skill-local references

## E. User Judgment Needed

本區已完成決策，保留作為歷史記錄：

下列資產是否保留、轉 skill、或改為 shared templates，仍需要使用者判斷：

- `.ai/assets/shared/validation-command-templates.md`
  - 疑似偏 template / operational snippet，而非 skill
- `.ai/assets/sub-agent-role-prompts/code-review-sub-agent/references/review-prompt.md`
  - 可能退役並由 `code-reviewer` skill 吸收
- `.ai/assets/sub-agent-role-prompts/aggregate-code-review-sub-agent/references/review-prompt.md`
  - 可能保留為專門 reference，也可能併入 reviewer references
- `.ai/assets/sub-agent-role-prompts/aggregate-test-sub-agent/references/test-generation-guidance.md`
  - 可能成為未來 test-generation skill 的 reference
- `.ai/assets/shared/contract-test-generation-guidance.md`
  - 同上
- `.ai/assets/sub-agent-role-prompts/controller-test-sub-agent/references/test-generation-guidance.md`
  - 同上
- `.ai/assets/sub-agent-role-prompts/reactor-test-sub-agent/references/test-generation-guidance.md`
  - 同上
- `.ai/assets/sub-agent-role-prompts/usecase-test-sub-agent/references/test-generation-guidance.md`
  - 同上

## F. Canonical Skill Reference Neutralization

目前至少下列 canonical skill specs 仍引用 `.claude/skills/.../references/`：

- `.ai/assets/skills/bdd-gwt-test-designer/skill.yaml`
- `.ai/assets/skills/staged-refactor-implementer/skill.yaml`
- `.ai/assets/skills/tactical-refactor-implementer/skill.yaml`

初步建議：

- 在 `.ai/assets/skills/<skill-id>/references/` 建立 canonical references
- 更新 `skill.yaml` 指向新的 canonical references
- Claude / Codex wrappers 改為引用 canonical references，而非反過來讓 canonical spec 依賴 Claude paths


