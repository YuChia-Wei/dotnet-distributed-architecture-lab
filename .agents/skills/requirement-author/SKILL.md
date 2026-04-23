---
name: requirement-author
description: Draft or normalize requirement documents for this repository from rough notes, existing requirement files, architecture references, or codebase facts. Use when Codex needs to turn unstructured problem statements into `.dev/requirement/`-aligned markdown without yet expanding into use-case specs.
---

# Requirement Author

This is a thin current-runtime wrapper.

## Canonical Source

- Registry: `.ai/assets/skills/README.MD`
- Spec: `.ai/assets/skills/requirement-author/skill.yaml`
- Human Guide: `.dev/guides/ai-collaboration-guides/REQUIREMENT-DESIGNER-PROMPT-GUIDE.md`
- References:
  - `.ai/assets/skills/requirement-author/references/authoring-playbook.md`
  - `.ai/assets/skills/requirement-author/references/output-contract.md`
  - `.ai/assets/skills/requirement-author/references/source-truth-rules.md`

## Wrapper Rules

Use this wrapper only as the current runtime entry.
Keep runtime-specific metadata in this wrapper directory only when the runtime requires it.
If wrapper text and canonical spec differ, follow `.ai/assets/skills/requirement-author/skill.yaml`.
