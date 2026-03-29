---
name: staged-refactor-implementer
description: Execute incremental refactoring stages in this repository using existing architecture decisions and review findings. Use when Codex needs to turn a bounded, pre-decided refactoring slice into concrete code changes, tests, and validation steps without redefining the overall architecture direction.
---

# Staged Refactor Implementer

## Overview

Use this skill after `ddd-ca-hex-architect` and/or `code-reviewer` have already defined the target direction.
Its job is to make one safe refactoring stage real: choose the smallest viable slice, change code incrementally, preserve behavior when possible, and leave a clean handoff for validation.

## Quick Start

1. Read `.dev/ARCHITECTURE.MD` and `.dev/requirement/TECH-STACK-REQUIREMENTS.MD`.
2. Read [references/skill-boundaries.md](references/skill-boundaries.md) to confirm this task belongs to implementation, not architecture planning or review.
3. Read [references/execution-playbook.md](references/execution-playbook.md) before making edits.
4. Read [references/input-contract.md](references/input-contract.md) to normalize the inputs from architect plans and review findings.
5. If the task targets a specific implementation area, load only the matching canonical sub-agent family under `.ai/assets/sub-agent-role-prompts/` plus relevant shared materials under `.ai/assets/shared/`.

## Workflow

### 1. Confirm the stage boundary
Before editing code, identify:
- current stage goal
- target module or files
- expected behavior to preserve
- explicit non-goals for this stage

### 2. Normalize inputs
Expected inputs may include:
- architecture target from `ddd-ca-hex-architect`
- findings from `code-reviewer`
- a user-defined refactoring slice
- explicit validation or test requirements

If the architecture target is still ambiguous, stop and send the task back to `ddd-ca-hex-architect` instead of guessing.
If review findings are missing, only proceed when the user has already provided a narrow, concrete stage goal and bounded scope.

### 3. Choose the smallest safe slice
Prefer one of these slices:
- extract one port or interface boundary
- separate one command/query responsibility
- move one adapter concern out of domain/application
- clean one aggregate boundary
- add tests needed to protect the stage

Avoid mixing unrelated cleanup or naming churn into the same stage.

Maximum default stage size:
- one aggregate boundary cleanup
- one command/query split for one use case
- one adapter extraction or one outbound port isolation
- one repository misuse cleanup in one module
- one targeted test-protection pass for one hot path

If the requested work is larger than this, split it into multiple stages or send it back to `ddd-ca-hex-architect`.

### 4. Implement incrementally
While editing:
- preserve behavior unless the stage explicitly changes it
- keep file scope bounded
- make dependencies more explicit, not less
- add or adjust tests only where the stage needs protection
- leave follow-up items clearly deferred instead of half-implementing them

### 5. Validate and hand off
At the end of the stage:
- summarize what changed
- note what remains for the next stage
- identify which areas should go back to `code-reviewer`
- identify whether any architecture assumptions should be re-checked with `ddd-ca-hex-architect`

## Execution Rules

### Scope Control
- Never turn a stage into a full rewrite.
- Prefer one coherent refactoring move over many loosely related edits.
- If a task spans too many modules, split it before implementing.
- Without enough input, restrict work to a very small, behavior-preserving refactor or stop.
- Default hard limit: one module slice, one aggregate slice, one use case flow, or one adapter move per stage.

### Architecture Discipline
- Follow the direction set by `ddd-ca-hex-architect`; do not invent a new target architecture mid-flight.
- Use `code-reviewer` findings as implementation constraints, not as a replacement for architecture planning.
- Respect repo rules around MQ-only cross-BC communication, DI, repository usage, and testing.
- Do not expand a vague request like "refactor this" into a broad redesign by yourself.

### Testing and Validation
- Keep or improve behavior protection for changed areas.
- If tests apply, run the smallest meaningful test scope first.
- If a test gap blocks safe refactoring, add the missing protection before bigger moves.

### Output Expectations
For each implementation stage, return:
1. chosen slice and reason
2. files changed or planned
3. behavior compatibility notes
4. tests or validation run
5. deferred follow-ups

If inputs are insufficient, return:
1. why the task is under-specified
2. whether it should go to `ddd-ca-hex-architect` or `code-reviewer`
3. the minimum additional input needed to proceed safely

## References

- [references/skill-boundaries.md](references/skill-boundaries.md)
- [references/execution-playbook.md](references/execution-playbook.md)
- [references/input-contract.md](references/input-contract.md)
