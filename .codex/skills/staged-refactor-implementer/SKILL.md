---
name: staged-refactor-implementer
description: Execute incremental refactoring stages in this repository using existing architecture decisions and review findings. Use it to turn one bounded, pre-decided refactoring slice into concrete code changes, tests, and validation steps.
---

# Staged Refactor Implementer

Use this as the Codex runtime skill wrapper for stage-level refactoring execution.

## Canonical Source

- `.ai/assets/skills/staged-refactor-implementer/skill.yaml`

## Human-Facing Guide

- `.dev/guides/ai-collaboration-guides/STAGED-REFACTOR-IMPLEMENTER-SKILL-GUIDE.md`

## Quick Start

1. Read `.dev/ARCHITECTURE.MD` and `.dev/requirement/TECH-STACK-REQUIREMENTS.MD`.
2. Read `.ai/assets/skills/staged-refactor-implementer/references/skill-boundaries.md`.
3. Read `.ai/assets/skills/staged-refactor-implementer/references/execution-playbook.md`.
4. Read `.ai/assets/skills/staged-refactor-implementer/references/input-contract.md`.

## Wrapper Rules

- Treat this file as a thin runtime wrapper only.
- Use `.ai/assets/skills/staged-refactor-implementer/skill.yaml` as the canonical source of truth.
- Keep the stage bounded; do not redefine architecture direction mid-flight.


