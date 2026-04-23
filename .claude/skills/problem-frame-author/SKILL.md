---
name: problem-frame-author
description: Draft a first problem frame for this repository from existing requirements, specs, ADRs, code, or tests. Use when Codex needs to create validator-ready CBF or SWF inputs, reverse-engineer a problem frame from code, or turn requirement/spec truth into structured problem-frame files without yet claiming spec compliance.
---

# Problem Frame Author

This is a thin Claude-compatible wrapper.

## Canonical Source

- Registry: `.ai/assets/skills/README.MD`
- Spec: `.ai/assets/skills/problem-frame-author/skill.yaml`
- Human Guide: `.dev/guides/ai-collaboration-guides/PROBLEM-FRAME-AUTHORING-GUIDE.md`
- References:
  - `.ai/assets/skills/problem-frame-author/references/authoring-playbook.md`
  - `.ai/assets/skills/problem-frame-author/references/source-mapping.md`
  - `.ai/assets/skills/problem-frame-author/references/output-contract.md`

## Wrapper Rules

Use this wrapper only as a compatibility entry.
Keep runtime-specific metadata in this wrapper directory only when the runtime requires it.
If wrapper text and canonical spec differ, follow `.ai/assets/skills/problem-frame-author/skill.yaml`.
