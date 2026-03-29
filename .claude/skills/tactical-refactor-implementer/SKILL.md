---
name: tactical-refactor-implementer
description: Execute local, object-centered refactoring in this repository. Use when Codex needs to improve one target class, object, or symbol through bounded structural changes such as extract method or safe local rename, without redesigning architecture, introducing new types, or planning a larger refactoring stage.
---

# Tactical Refactor Implementer

## Overview

Use this skill for tactical refactoring around one main target.
It is for local structure improvement, not architecture design and not stage-level refactoring.

## Quick Start

1. Read `.dev/ARCHITECTURE.MD` and `.dev/requirement/TECH-STACK-REQUIREMENTS.MD`.
2. Read [references/skill-boundaries.md](references/skill-boundaries.md) to confirm this is a local refactor task.
3. Read [references/allowed-operations.md](references/allowed-operations.md) to confirm the requested operation is in scope.
4. Read [references/execution-rules.md](references/execution-rules.md) before editing.

## Workflow

### 1. Confirm the main target
Identify exactly one primary target:
- class
- object
- symbol to rename

### 2. Confirm the local operation
Allowed default operations:
- extract method
- rename symbol

Do not introduce a new class or a new interface in this skill.
If the refactor requires a new type, redirect to `ddd-ca-hex-architect` for review and then to `staged-refactor-implementer` for execution.

### 3. Set the dependency radius
The default dependency radius is:
- target class/object
- direct dependencies
- direct call sites
- immediate tests if needed

Do not silently expand past this radius.

### 4. Apply one coherent local refactor
Prefer a single coherent local move over several loosely related edits.
If the task starts requiring module boundaries or architecture changes, stop and redirect.

## Scope Rules

### What This Skill Owns
- local structural refactoring
- object-centered cleanup
- direct dependency updates
- safe bounded renames

### What This Skill Does Not Own
- architecture redesign
- stage-level refactoring strategy
- aggregate or bounded context re-cutting
- new class extraction
- new interface extraction
- broad multi-module cleanup campaigns

### Maximum Default Size
- one primary target
- one main refactoring operation
- only direct dependencies and direct call sites

## Output Expectations

Return:
1. target and chosen operation
2. files changed or planned
3. dependency radius touched
4. behavior compatibility notes
5. deferred items if broader work is needed

## References

- [references/skill-boundaries.md](references/skill-boundaries.md)
- [references/allowed-operations.md](references/allowed-operations.md)
- [references/execution-rules.md](references/execution-rules.md)
