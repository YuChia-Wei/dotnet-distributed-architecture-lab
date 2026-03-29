---
name: code-reviewer
description: Review .NET code in this repository for DDD, Clean Architecture, CQRS, and Event Sourcing compliance. This skill reviews, scores, and marks issues; it does not plan refactors or define target architecture.
---

# Code Reviewer

Use this as the Codex runtime skill wrapper for repository code review.

## Canonical Source

- `.ai/assets/skills/code-reviewer/skill.yaml`

## Human-Facing Guide

- `.dev/guides/ai-collaboration-guides/AI-REFACTORING-SKILL-BOUNDARY-GUIDE.md`

## Quick Start

1. Read `.ai/CODE-REVIEW-INDEX.MD`.
2. Read `.claude/skills/code-reviewer/CHECKLIST-REFERENCE.MD`.
3. Read `.dev/standards/CODE-REVIEW-CHECKLIST.md`.
4. Read the target file and build a checklist comparison.

## Wrapper Rules

- Treat this file as a thin runtime wrapper only.
- Use `.ai/assets/skills/code-reviewer/skill.yaml` as the canonical source of truth.
- Review, score, and mark issues only.
- Do not output staged refactoring plans or target architecture design.
