# Skill Boundaries

Use this file to decide whether the task belongs to `tactical-refactor-implementer`.

## Use This Skill When

- the user wants local, object-centered refactoring
- there is one primary target class, object, or symbol
- the work is mostly extract-method/rename/restructure, not architecture redesign
- only direct dependencies and immediate call sites need updates
- no new class or interface needs to be introduced

## Do Not Use This Skill When

- the task requires bounded context or aggregate redesign
- the task spans multiple modules as a coordinated stage
- the task is primarily architecture planning
- the task is primarily code review
- the task requires extracting a new class or interface
- the rename changes domain language or boundary semantics

## Routing

- `ddd-ca-hex-architect`: architecture direction
- `code-reviewer`: findings and scoring
- `staged-refactor-implementer`: stage-level/module-level refactor execution
- `tactical-refactor-implementer`: local class/object/symbol refactoring
