---
name: reactor-implementer
description: Implement a bounded reactor in this repository for event-driven consistency, projection updates, or integration reactions without redefining the architecture direction.
---

# Reactor Implementer

This is a thin Claude-compatible wrapper.

## Canonical Source

- Registry: `.ai/assets/skills/README.MD`
- Spec: `.ai/assets/skills/reactor-implementer/skill.yaml`
- Human Guide: `.dev/guides/ai-collaboration-guides/USE-CASE-IMPLEMENTER-SKILL-GUIDE.md`
- References:
  - `.ai/assets/skills/reactor-implementer/references/implementation-playbook.md`
  - `.ai/assets/skills/reactor-implementer/references/handoff-rules.md`
  - `.ai/assets/sub-agent-role-prompts/reactor-sub-agent/sub-agent.yaml`

## Wrapper Rules

Use this wrapper only as a compatibility entry.
Keep runtime-specific metadata in this wrapper directory only when the runtime requires it.
If wrapper text and canonical spec differ, follow `.ai/assets/skills/reactor-implementer/skill.yaml`.
