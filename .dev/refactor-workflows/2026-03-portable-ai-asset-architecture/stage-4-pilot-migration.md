# Stage 4 Pilot Migration

本階段完成兩個 pilot：

- skill pilot: `ddd-ca-hex-architect`
- command family pilot: `command-sub-agent` / `query-sub-agent` / `reactor-sub-agent`

## Pilot Goal

驗證下列三層是否可以共存：

1. canonical source
2. human-facing guide
3. multi-agent wrappers

## Skill Pilot

### Canonical Source

- `.ai/assets/skills/ddd-ca-hex-architect/skill.yaml`
- `.ai/assets/skills/ddd-ca-hex-architect/references/*`

### Human Guide

- `.dev/guides/ai-collaboration-guides/DDD-CA-HEX-ARCHITECT-SKILL-GUIDE.md`

### Wrappers

- `.claude/skills/ddd-ca-hex-architect/`
- `.codex/prompts/ddd-ca-hex-architect.md`
- `.gemini/commands/ddd-ca-hex-architect.md`
- `.github/prompts/ddd-ca-hex-architect.md`

## Command Family Pilot

本節記錄的是 pilot migration 當時的中間狀態。最終結果是 `.ai/assets/commands/` 與 shared prompt-package 已移除，並由 canonical sub-agent-role assets 承接。

### Canonical Source

- 歷史中介層：
  - `.ai/assets/commands/command-sub-agent/command.yaml`
  - `.ai/assets/commands/query-sub-agent/command.yaml`
  - `.ai/assets/commands/reactor-sub-agent/command.yaml`
  - `.ai/assets/shared/prompt-packages/dotnet-usecase-sub-agents/package.yaml`
- 最終 canonical source：
  - `.ai/assets/sub-agent-role-prompts/command-sub-agent/sub-agent.yaml`
  - `.ai/assets/sub-agent-role-prompts/query-sub-agent/sub-agent.yaml`
  - `.ai/assets/sub-agent-role-prompts/reactor-sub-agent/sub-agent.yaml`

### Wrappers

- `.codex/prompts/command-sub-agent.md`
- `.codex/prompts/query-sub-agent.md`
- `.codex/prompts/reactor-sub-agent.md`
- `.gemini/commands/command-sub-agent.md`
- `.gemini/commands/query-sub-agent.md`
- `.gemini/commands/reactor-sub-agent.md`
- `.github/prompts/command-sub-agent.md`
- `.github/prompts/query-sub-agent.md`
- `.github/prompts/reactor-sub-agent.md`

## Validation

- Canonical source 已獨立於 wrapper roots
- human-facing guide 仍保留於 `.dev/guides/ai-collaboration-guides/`
- Codex / Gemini / Copilot 都有 repo-level wrapper entry
- Claude skill 仍保留既有 runtime-compatible skill root
