---
name: spec-compliance-validator
description: |
  Validate .NET code and tests against problem frame specs with a 100% gate.
  Supports CBF (CommandedBehaviorFrame) and SWF (SimpleWorkpieceFrame).
  Use when: "validate spec dotnet", "check compliance dotnet", "spec-compliance-validator"
allowed-tools: Read, Glob, Grep, Bash, TodoWrite
---

# Spec Compliance Validator Skill (.NET)

This is a thin current-runtime wrapper.

## Canonical Source

- Registry: `.ai/assets/skills/README.MD`
- Spec: `.ai/assets/skills/spec-compliance-validator/skill.yaml`
- Human Guide: `.dev/guides/ai-collaboration-guides/AI-COLLABORATION-WORKFLOW-GUIDE.md`
- References:
  - `.ai/assets/skills/spec-compliance-validator/references/spec-compliance-rules.md`
  - `.ai/assets/skills/spec-compliance-validator/references/test-validation-steps.md`
  - `.ai/assets/skills/spec-compliance-validator/references/validation-command-templates.md`

## Wrapper Rules

Use this wrapper only as the current runtime entry.
Keep runtime-specific metadata in this wrapper directory only when the runtime requires it.
If wrapper text and canonical spec differ, follow `.ai/assets/skills/spec-compliance-validator/skill.yaml`.


