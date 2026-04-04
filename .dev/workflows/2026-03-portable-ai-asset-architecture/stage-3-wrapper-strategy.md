# Stage 3 Wrapper Strategy

本階段定義多 agent 的 repo-level wrapper strategy，目標是在不複製完整 canonical content 的前提下，提供各 agent 可讀取的最小入口。

## Wrapper Roots

### Claude

- Wrapper root:
  - `.claude/skills/`
- Wrapper unit:
  - `<skill-id>/SKILL.md`
- Current role:
  - skill-oriented wrapper

### Codex

- Wrapper root:
  - `.codex/prompts/`
- Wrapper unit:
  - `<command-or-skill>.md`
- Current role:
  - prompt-oriented wrapper

### Gemini

- Wrapper root:
  - `.gemini/commands/`
- Context file:
  - `.gemini/settings.json`
- Wrapper unit:
  - `<command>.md`
- Current role:
  - command-oriented wrapper

### GitHub Copilot

- Wrapper root:
  - `.github/prompts/`
- Context / instruction file:
  - `.github/copilot-instructions.md`
- Wrapper unit:
  - `<command-or-workflow>.md`
- Current role:
  - prompt/instructions-oriented wrapper

## Wrapper Principles

- wrapper 必須薄
- wrapper 不應重複完整 canonical content
- wrapper 應只包含：
  - agent-specific invocation syntax
  - 最小 trigger / entry wording
  - 指向 canonical source 的引用
  - 必要的 runtime metadata

## Mapping Model

### Skill Wrapper

對應來源：

- `.ai/assets/skills/<skill-id>/skill.yaml`

可被 wrapper 重述的內容：

- title
- purpose 摘要
- trigger phrases
- human guide path

應引用而非複製的內容：

- 完整 workflow
- 詳細 constraints
- 大量 reference material
- examples

### Command Wrapper

本節為歷史設計快照；最終 command layer 已退役，delegated wrapper 應直接指向 canonical sub-agent assets。

歷史對應來源：

- `.ai/assets/commands/<command-id>/command.yaml`

最終對應來源：

- `.ai/assets/sub-agent-role-prompts/<sub-agent-id>/sub-agent.yaml`

可被 wrapper 重述的內容：

- command title
- usage summary
- entry syntax

應引用而非複製的內容：

- prompt package 全文
- shared rules 全文
- long examples

## Wrapper Content Pattern

### Thin Pointer Wrapper

適用於：

- 已有完整 canonical source
- agent 只需要短入口

內容應包含：

- wrapper title
- short purpose
- canonical source path
- optional human guide path

### Thin Prompt Wrapper

適用於：

- agent 需要以 prompt file 作為入口

內容應包含：

- concise invocation prompt
- canonical source path
- shared package path

## Repo Changes Required

本階段應建立或確認以下 wrapper interfaces：

- `.claude/skills/`
- `.codex/prompts/`
- `.gemini/commands/`
- `.github/prompts/`
- `.github/copilot-instructions.md`

## Git Tracking Note

`.gitignore` 目前對 `.codex/*` 的規則只明確放行 `.codex/prompts/` 目錄本身。  
若要追蹤 `.codex/prompts/` 內的 wrapper files，需額外放行：

- `!/.codex/prompts/**`

## Stage 3 Output

本階段完成後，應至少具備：

- wrapper roots 明確化
- `.gitignore` 允許 repo 追蹤 `.codex/prompts/` wrapper files
- 各 agent 的 wrapper 粒度與內容原則固定
