---
name: query-use-case-implementer
description: Implement a bounded query-side use case in this repository from requirement, spec, architecture decisions, or review findings without drifting into architecture redesign.
---

# Query Use Case Implementer

This is a thin Claude-compatible wrapper.

## Canonical Source

- Registry: `.ai/assets/skills/README.MD`
- Spec: `.ai/assets/skills/query-use-case-implementer/skill.yaml`
- Human Guide: `.dev/guides/ai-collaboration-guides/USE-CASE-IMPLEMENTER-SKILL-GUIDE.md`
- References:
  - `.ai/assets/skills/query-use-case-implementer/references/implementation-playbook.md`
  - `.ai/assets/skills/query-use-case-implementer/references/handoff-rules.md`
  - `.ai/assets/sub-agent-role-prompts/query-sub-agent/sub-agent.yaml`

## Wrapper Rules

Use this wrapper only as a compatibility entry.
Keep runtime-specific metadata in this wrapper directory only when the runtime requires it.
If wrapper text and canonical spec differ, follow `.ai/assets/skills/query-use-case-implementer/skill.yaml`.
