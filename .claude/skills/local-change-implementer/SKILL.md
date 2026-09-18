---
name: local-change-implementer
description: Execute one local class, object, method, symbol, SQL/ORM, or direct-call-site technical change without introducing new architecture boundaries or broadening into a slice.
---

# Local Change Implementer

This is a thin Claude-compatible wrapper.

## Canonical Source

- Registry: `.ai/assets/skills/README.MD`
- Spec: `.ai/assets/skills/local-change-implementer/skill.yaml`
- Human Guide: `.dev/guides/ai-collaboration-guides/LOCAL-CHANGE-IMPLEMENTER-SKILL-GUIDE.md`
- References:
  - `.ai/assets/skills/local-change-implementer/references/allowed-operations.md`
  - `.ai/assets/skills/local-change-implementer/references/execution-rules.md`
  - `.ai/assets/skills/local-change-implementer/references/skill-boundaries.md`

## Wrapper Rules

Use this wrapper only as a compatibility entry.
Keep runtime-specific metadata in this wrapper directory only when the runtime requires it.
If wrapper text and canonical spec differ, follow `.ai/assets/skills/local-change-implementer/skill.yaml`.
