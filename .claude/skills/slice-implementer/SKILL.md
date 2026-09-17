---
name: slice-implementer
description: Implement one bounded command, query, reactor or generic slice under accepted architecture. Retain slice ownership for internal local edits and hand off only for a concrete missing decision or separable useful subtask.
---

# Slice Implementer

This is a thin Claude-compatible wrapper.

## Canonical Source

- Registry: `.ai/assets/skills/README.MD`
- Spec: `.ai/assets/skills/slice-implementer/skill.yaml`
- Human Guide: `.dev/guides/ai-collaboration-guides/SLICE-IMPLEMENTER-SKILL-GUIDE.md`
- References:
  - `.ai/assets/shared/IMPLEMENTATION-SCOPE-ROUTING-CONTRACT.md`
  - `.ai/assets/skills/slice-implementer/references/input-contract.md`
  - `.ai/assets/skills/slice-implementer/references/execution-playbook.md`
  - `.ai/assets/skills/slice-implementer/references/role-execution.md`
  - `.ai/assets/skills/slice-implementer/references/handoff-rules.md`
  - `.ai/assets/skills/slice-implementer/references/modes/command-use-case.md`
  - `.ai/assets/skills/slice-implementer/references/modes/query-use-case.md`
  - `.ai/assets/skills/slice-implementer/references/modes/reactor.md`
  - `.ai/assets/skills/slice-implementer/references/modes/generic-slice.md`
  - `.ai/assets/skills/slice-implementer/references/overlays/remediation.md`

## Wrapper Rules

Use this wrapper only as a compatibility entry.
Keep runtime-specific metadata in this wrapper directory only when the runtime requires it.
If wrapper text and canonical spec differ, follow `.ai/assets/skills/slice-implementer/skill.yaml`.
