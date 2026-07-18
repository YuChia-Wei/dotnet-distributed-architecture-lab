---
name: code-reviewer
description: |
  Review .NET code for DDD, Clean Architecture, CQRS, and Event Sourcing compliance.
  Use when: user asks to "code review", "review code", "check this file",
  mentions reviewing a specific C# file, or asks about code quality. This skill only reviews,
  scores, and marks issues; persisted large reviews use standalone assessments. It does not
  plan refactors, implement fixes, or define target architecture.
allowed-tools: Read, Glob, Grep, Bash
---

# Code Reviewer Skill (.NET)

This is a thin current-runtime wrapper.

## Canonical Source

- Registry: `.ai/assets/skills/README.MD`
- Spec: `.ai/assets/skills/code-reviewer/skill.yaml`
- Human Guide: `.dev/guides/ai-collaboration-guides/AI-REFACTORING-SKILL-BOUNDARY-GUIDE.md`
- References:
  - `.ai/assets/tech-stacks/dotnet-backend/references/CODE-REVIEW-INDEX.MD`
  - `.ai/assets/skills/code-reviewer/references/checklist-reference.md`
  - `.ai/assets/skills/code-reviewer/references/output-contract.md`
  - `.dev/standards/CODE-REVIEW-CHECKLIST.md`
  - `.dev/standards/ASSESSMENT-ARTIFACT-POLICY.md`
- Report Template: `.ai/assets/skills/code-reviewer/templates/code-review-assessment-report-template.md`

## Wrapper Rules

Use this wrapper only as the current runtime entry.
Keep runtime-specific metadata in this wrapper directory only when the runtime requires it.
If wrapper text and canonical spec differ, follow `.ai/assets/skills/code-reviewer/skill.yaml`.

## Validation Boundary

Use software engineering reasoning and checklist comparison as the core review method.
Analyzer, architecture test, and dotnet test output may support the review when available.
Do not treat transitional `.ai/scripts` grep-based C# checks as final semantic validation.
Return ordinary reviews in conversation. Persist a review only when requested, using
`.dev/assessments/<ASM-YYYYMMDD-NNN>/`, and keep remediation outside this skill.
