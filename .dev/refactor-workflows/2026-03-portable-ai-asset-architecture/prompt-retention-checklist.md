# Prompt Retention Checklist

## A. Decisions To Lock

- [x] `.codex/commands/` 不再保留
- [x] `.codex/skills/` 為 Codex 唯一 runtime wrapper root
- [x] `.codex/skills/` 暫不導入 sync/export tooling
- [x] `.ai/assets/commands/` 已自 repo 移除
- [x] command/query/reactor 的 sub-agent-role-prompt migration strategy 定稿
- [ ] `.claude/skills/.../references/` 遷移策略定稿
- [x] use-case sub-agent 不應建模成 top-level skill
- [x] use-case sub-agent 的 canonical source 改定義在 `.ai/assets/sub-agent-role-prompts/`
- [x] command/query/reactor 的 top-level skill 化判定為 provisional 並已回退
- [ ] delegated sub-agent wrapper strategy 定稿

## B. Command-Style Prompt Migration

- [x] `aggregate-sub-agent-prompt.md` 收斂為 `sub-agent-role-prompts/aggregate-sub-agent`
- [x] `command-sub-agent-prompt.md` 收斂為 `sub-agent-role-prompts/command-sub-agent`
- [x] `query-sub-agent-prompt.md` 收斂為 `sub-agent-role-prompts/query-sub-agent`
- [x] `reactor-sub-agent-prompt.md` 收斂為 `sub-agent-role-prompts/reactor-sub-agent`
- [x] `frontend-sub-agent-prompt.md` 收斂為 `sub-agent-role-prompts/frontend-sub-agent`
- [x] `mutation-testing-sub-agent-prompt.md` 收斂為 `sub-agent-role-prompts/mutation-testing-sub-agent`
- [x] `outbox-sub-agent-prompt.md` 收斂為 `sub-agent-role-prompts/outbox-sub-agent`
- [x] `profile-config-sub-agent-prompt.md` 收斂為 `sub-agent-role-prompts/profile-config-sub-agent`

## C. Keep As Shared / Explanatory Materials

- [x] `PROMPT-PORTABILITY-RULES.md` 保留於 `.ai/assets/` 作為 shared portability policy
- [x] `spec-compliance-rules.md` 保留於 `.ai/assets/` 作為 spec-compliance supporting material
- [x] `test-validation-steps.md` 保留於 `.ai/assets/` 作為 validation checklist material
- [x] `testing-standards-prompt.md` 保留於 `.ai/assets/` 作為 shared testing rules summary
- [x] `code-review-checklist.md` 保留於 `.ai/assets/` 作為 delegated review / top-level review 共用 checklist
- [x] `.ai/assets/shared/*` 長期保留為 shared rule fragments，不升格為 skill 或 sub-agent taxonomy

## D. User Judgment Queue

- [x] `validation-command-templates.md` 保留為 shared validation/report template material
- [x] `code-review-prompt.md` 收斂為 `sub-agent-role-prompts/code-review-sub-agent`
- [x] `aggregate-code-review-prompt.md` 收斂為 `sub-agent-role-prompts/aggregate-code-review-sub-agent`
- [x] `aggregate-test-generation-prompt.md` 收斂為 `sub-agent-role-prompts/aggregate-test-sub-agent`
- [x] `contract-test-generation-prompt.md` 保留為 DBC 專用 supporting material，待未來規範成熟後再評估
- [x] `controller-test-generation-prompt.md` 收斂為 `sub-agent-role-prompts/controller-test-sub-agent`
- [x] `reactor-test-generation-prompt.md` 收斂為 `sub-agent-role-prompts/reactor-test-sub-agent`
- [x] `usecase-test-generation-prompt.md` 收斂為 `sub-agent-role-prompts/usecase-test-sub-agent`
- [x] `controller-code-review-prompt.md` 收斂為 `sub-agent-role-prompts/controller-code-review-sub-agent`
- [x] `reactor-code-review-prompt.md` 收斂為 `sub-agent-role-prompts/reactor-code-review-sub-agent`

## E. Canonical Reference Neutralization

- [x] `bdd-gwt-test-designer` references 搬到 `.ai/assets/skills/.../references/`
- [x] `staged-refactor-implementer` references 搬到 `.ai/assets/skills/.../references/`
- [x] `tactical-refactor-implementer` references 搬到 `.ai/assets/skills/.../references/`
- [x] canonical skill specs 更新為新的 references paths
- [x] wrapper docs 驗證未引入第二份真相

## F. Documentation Update

- [x] AI asset strategy 文件改為 skill-first, command-retirement wording
- [x] local runtime guide 補上「不提供 sync/export tooling」說明
- [x] indexes 移除不再主打 command-spec 的描述
- [x] active sub-agent docs 改為 sub-agent-role-prompt taxonomy，並記錄 corrected canonical source
- [x] remaining active legacy command-spec / prompt-package references 已明確標示為 transition layer 並指向 skill-first primary entries
- [x] active docs 改為 sub-agent-role-prompt taxonomy，移除 command/query/reactor top-level skill 說法


