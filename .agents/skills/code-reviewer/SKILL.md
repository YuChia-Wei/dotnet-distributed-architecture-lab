---
name: code-reviewer
description: |
  Review code through a technology-neutral core, selected technology extensions
  and target-owned rules. Use for code review, implementation-guidance review,
  specific files or code-quality questions. Return evidence-backed findings and
  coverage limitations; do not implement fixes, plan refactors or define architecture.
allowed-tools: Read, Glob, Grep, Bash
---

# Code Reviewer Skill

This is a thin current-runtime wrapper.

## Canonical Source

- Registry: `.ai/assets/skills/README.MD`
- Spec: `.ai/assets/skills/code-reviewer/skill.yaml`
- Human Guide: `.dev/guides/ai-collaboration-guides/AI-REFACTORING-SKILL-BOUNDARY-GUIDE.md`
- References:
  - `.ai/assets/skills/code-reviewer/references/review-routing.yaml`
- Report Template: `.ai/assets/skills/code-reviewer/templates/code-review-assessment-report-template.md`

## Wrapper Rules

Use this wrapper only as the current runtime entry.
Keep runtime-specific metadata in this wrapper directory only when the runtime requires it.
If wrapper text and canonical spec differ, follow `.ai/assets/skills/code-reviewer/skill.yaml`.

## Validation Boundary

Select the common route and applicable installed extensions before loading their
rules. Use behavior, contracts and evidence for review reasoning; report missing
specialist coverage. Applicable effective-rule preflight remains fail-closed.
Tests and analyzers support the review only when actually available and authorized.
Return ordinary reviews in conversation. Persist a review only when requested,
using `.dev/assessments/<ASM-YYYYMMDD-HH-xxx>/`, and keep remediation outside this skill.
