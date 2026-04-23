---
name: spec-author
description: Draft or normalize production specs and test specs for this repository from requirements, existing specs, or codebase facts. Use when Codex needs to turn requirement truth into `.dev/specs/`-aligned JSON or markdown without yet claiming code or test completion.
---

# Spec Author

This is a thin Claude-compatible wrapper.

## Canonical Source

- Registry: `.ai/assets/skills/README.MD`
- Spec: `.ai/assets/skills/spec-author/skill.yaml`
- Human Guide: `.dev/guides/ai-collaboration-guides/SPEC-DESIGNER-PROMPT-GUIDE.md`
- References:
  - `.ai/assets/skills/spec-author/references/authoring-playbook.md`
  - `.ai/assets/skills/spec-author/references/output-contract.md`
  - `.ai/assets/skills/spec-author/references/type-selection.md`

## Wrapper Rules

Use this wrapper only as a compatibility entry.
Keep runtime-specific metadata in this wrapper directory only when the runtime requires it.
If wrapper text and canonical spec differ, follow `.ai/assets/skills/spec-author/skill.yaml`.
