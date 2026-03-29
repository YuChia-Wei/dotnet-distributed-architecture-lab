# Skill Boundaries

Use this file to decide whether the task belongs to `staged-refactor-implementer` or should be redirected.

## Use This Skill When

- the target architecture is already mostly decided
- the refactoring work can be expressed as one bounded stage
- review findings already exist, or the user has identified a concrete slice
- the next step is implementation, not diagnosis
- the scope is narrow enough that one stage can be reviewed and validated independently
- the stage fits within one module slice, one aggregate slice, one use case flow, or one adapter move

## Do Not Use This Skill When

- the user is still asking what the architecture should become
- the task is primarily a code review
- the change requires a new system-wide architecture decision first
- the scope is so broad that no bounded stage can be identified
- the request is just "refactor this" without a concrete stage goal, bounded scope, or explicit constraints
- the stage mixes multiple aggregates, multiple modules, or multiple unrelated architectural moves without prior decomposition

## Fallback Rule

If `ddd-ca-hex-architect` or `code-reviewer` inputs are missing:

- proceed only for a narrow, low-risk, behavior-preserving slice
- otherwise redirect the task

Do not compensate for missing planning by broadening the implementation scope.

## Skill Routing

- `ddd-ca-hex-architect`: diagnose and design
- `code-reviewer`: inspect and judge
- `staged-refactor-implementer`: execute one stage safely
