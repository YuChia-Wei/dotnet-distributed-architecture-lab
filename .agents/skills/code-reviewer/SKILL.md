---
name: code-reviewer
description: |
  Review .NET code for DDD, Clean Architecture, CQRS, and Event Sourcing compliance.
  Use when: user asks to "code review", "review code", "check this file",
  mentions reviewing a specific C# file, or asks about code quality. This skill only reviews,
  scores, and marks issues; it does not plan refactors or define target architecture.
allowed-tools: Read, Glob, Grep, Bash
---

# Code Reviewer Skill (.NET)

This is a thin current-runtime wrapper.

## Canonical Source

- Registry: `.ai/assets/skills/README.MD`
- Spec: `.ai/assets/skills/code-reviewer/skill.yaml`
- Human Guide: `.dev/guides/ai-collaboration-guides/AI-REFACTORING-SKILL-BOUNDARY-GUIDE.md`
- References:
  - `.ai/CODE-REVIEW-INDEX.MD`
  - `.ai/assets/skills/code-reviewer/references/checklist-reference.md`
  - `.dev/standards/CODE-REVIEW-CHECKLIST.md`

## Wrapper Rules

Use this wrapper only as the current runtime entry.
Keep runtime-specific metadata in this wrapper directory only when the runtime requires it.
If wrapper text and canonical spec differ, follow `.ai/assets/skills/code-reviewer/skill.yaml`.
