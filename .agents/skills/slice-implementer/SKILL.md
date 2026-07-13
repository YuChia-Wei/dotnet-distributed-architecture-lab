---
name: slice-implementer
description: Implement one bounded implementation slice from requirements, specs, architecture decisions, review findings, or workflow tasks using mode references such as command, query, reactor, generic, remediation, or refactor without redefining architecture direction.
---

# Slice Implementer

This is a thin current-runtime wrapper.

## Canonical Source

- Registry: `.ai/assets/skills/README.MD`
- Spec: `.ai/assets/skills/slice-implementer/skill.yaml`
- Human Guide: `.dev/guides/ai-collaboration-guides/SLICE-IMPLEMENTER-SKILL-GUIDE.md`
- References:
  - `.ai/assets/skills/slice-implementer/references/input-contract.md`
  - `.ai/assets/skills/slice-implementer/references/execution-playbook.md`
  - `.ai/assets/skills/slice-implementer/references/handoff-rules.md`
  - `.ai/assets/skills/slice-implementer/references/modes/command-use-case.md`
  - `.ai/assets/skills/slice-implementer/references/modes/query-use-case.md`
  - `.ai/assets/skills/slice-implementer/references/modes/reactor.md`
  - `.ai/assets/skills/slice-implementer/references/modes/generic-slice.md`

## Wrapper Rules

Use this wrapper only as the current runtime entry.
Keep runtime-specific metadata in this wrapper directory only when the runtime requires it.
If wrapper text and canonical spec differ, follow `.ai/assets/skills/slice-implementer/skill.yaml`.
