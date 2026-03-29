# AI Assets

本目錄是 portable AI assets 的 canonical source 根目錄。

## 目標

- 保存跨 agent 可重用的單一真相
- 讓 top-level skill、delegated sub-agent role、shared/supporting materials 有中立結構
- 避免各個 agent runtime wrapper 各自維護完整副本

## 目錄結構

```text
.ai/assets/
  skills/
  sub-agent-role-prompts/
  shared/
  templates/
```

## 子目錄分工

- `skills/`
  - canonical skill specs
- `sub-agent-role-prompts/`
  - canonical delegated worker-role definitions
- `shared/`
  - shared rules、contracts、templates、prompt packages、supporting materials
- `templates/`
  - canonical spec templates

## 與其他目錄的分工

- `.ai/assets/`
  - canonical source
- `.codex/skills/`
  - current primary repo-local runtime wrappers
- other agent-specific wrapper roots
  - optional compatibility layers; they may be absent in some environments and do not affect the canonical source model
- `.dev/guides/ai-collaboration-guides/`
  - human-facing usage guides
- `.dev/refactor-workflows/`
  - migration / refactor artifacts

## Current Direction

- `skills/` 是 top-level runtime capability 的 canonical source
- `sub-agent-role-prompts/` 是 delegated worker-role 的 canonical source
- `shared/` 與 `sub-agent-role-prompts/*/references/` 承接 reusable supporting materials
- `.gemini/commands/`、`.github/prompts/`、`.claude/skills/` 若存在，應視為 wrapper / compatibility layer，而不是 canonical source

