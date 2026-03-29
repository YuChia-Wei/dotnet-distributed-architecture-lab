# Sub-Agent Asset Strategy Correction

## Purpose

這份文件修正 Stage G 先前把 `*-sub-agent-prompt.md` 直接收斂成 top-level skill 的設計判斷。

## Corrected Conclusion

`*-sub-agent-prompt.md` 不應直接建模成 top-level skill。

它們較適合的 canonical 類型是：

- sub-agent role prompt
- delegation template
- worker-role prompt asset

## Why The Previous Direction Was Wrong

先前把 `command/query/reactor` 直接轉成 `.ai/assets/skills/...` 與 `.codex/skills/...`，雖然符合 runtime entry 想要收斂成 skill-first 的表象，但混淆了兩層：

1. top-level skills
2. delegated sub-agent role prompts

這會讓：

- user-facing / main-agent-facing capability
- delegated worker-role prompt

混成同一類 canonical asset。

## Corrected Taxonomy

### 1. Top-Level Skill

定義：

- 使用者或 main agent 會直接呼叫的能力
- 對 repo 協作流程具有高層決策、審查、設計、驗證、重構執行角色

目前保留為 top-level skills 的類型：

- `ddd-ca-hex-architect`
- `code-reviewer`
- `spec-compliance-validator`
- `staged-refactor-implementer`
- `tactical-refactor-implementer`
- `bdd-gwt-test-designer`

Canonical source:

- `.ai/assets/skills/`

### 2. Sub-Agent Role Prompt

定義：

- main agent 用來委派 bounded task 的 worker-role prompt asset
- 描述 delegated sub-agent 的角色、責任、輸入輸出、限制與 references
- 不應視為 top-level skill

Canonical source:

- `.ai/assets/sub-agent-role-prompts/`

推薦 schema：

- `sub-agent.yaml`
- `references/`

### 3. Shared Prompt Package

定義：

- 被多個 skill 或 sub-agent role 共用的 prompt fragments、shared rules、templates
- 不是獨立 runtime entry

Canonical source:

- `.ai/assets/shared/`
- `.ai/assets/shared/`

## Corrected Direction For Command / Query / Reactor

下列三者應收斂為 sub-agent role prompts，而非 top-level skills：

- `command-sub-agent`
- `query-sub-agent`
- `reactor-sub-agent`

因此：

- `.ai/assets/skills/command-use-case-implementer/` 應回退
- `.ai/assets/skills/query-use-case-implementer/` 應回退
- `.ai/assets/skills/reactor-implementer/` 應回退
- 對應 `.codex/skills/` 與 `.claude/skills/` wrappers 應移除

改由：

- `.ai/assets/sub-agent-role-prompts/command-sub-agent/`
- `.ai/assets/sub-agent-role-prompts/query-sub-agent/`
- `.ai/assets/sub-agent-role-prompts/reactor-sub-agent/`

承接 canonical source。

## Wrapper Strategy Correction

### Codex / Claude

- 不應把這三個 use-case sub-agents 當成 top-level skills 放進 `.codex/skills/` 或 `.claude/skills/`
- 若未來需要 delegated runtime wrapper，應在專門的 sub-agent wrapper strategy 中處理
- 在這個修正階段，先不為它們建立新的 top-level runtime wrappers

### Gemini / GitHub

- 目前保留 migration-time compatibility wrappers
- wrappers 應指向 corrected canonical source：
  - `.ai/assets/sub-agent-role-prompts/<id>/sub-agent.yaml`
- 舊 command-spec 已於後續清理階段自 repo 移除

## Naming Direction

`.ai/assets/commands/` 不再適合作為這批資產的最終 canonical 類別。

這批資產的更合理名稱是：

- `.ai/assets/sub-agent-role-prompts/`

而 `.ai/assets/commands/` 已確認不再作為 canonical 類別，並已於後續清理階段自 repo 移除。


