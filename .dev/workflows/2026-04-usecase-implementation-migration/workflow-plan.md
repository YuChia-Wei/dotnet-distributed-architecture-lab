# Workflow Plan

## Metadata

- `plan_id`: `workflow-plan-2026-04-usecase-implementation-migration`
- `owner_skill`: `staged-refactor-implementer`
- `status`: `completed`

## Commit Strategy

- Expected commit checkpoints:
  - Workflow rule updates and governance adjustments.
  - Product bounded context migration slice.
  - Order bounded context migration slice.
  - Inventory bounded context migration slice.
- Commit rule:
  - Each bounded-context slice must be committed after minimal validation instead of waiting for the whole migration to finish.
- Notes:
  - If environment issues block full validation, record the blocker in workflow artifacts and still commit the independently reviewable slice.

## Context

- Problem statement:
  - The repository guideline now defines `Use Case` as the explicit application inbound port for HTTP entry, but the current codebase still uses `command/query + handler + message bus` as the default application boundary.
- Current scope:
  - Rename existing command/query objects where they are acting as the effective HTTP use case input and execution unit.
  - Introduce explicit use case types and update controller invocation style.
  - Keep message-oriented flows working where they are still required.
- Why this workflow now:
  - The terminology decision has been approved and documented.
  - Implementation now needs to converge on the new boundary model before more code is added on top of the old pattern.

## Target Direction

- Target architecture summary:
  - HTTP controllers should use explicit `Use Case` ports via `[FromServices]`.
  - Existing `Command` / `Query` / `Handler` symbols that currently behave as the main HTTP boundary should be migrated to `UseCase` / `Input` / `Output`.
  - Result Pattern use cases should use `Result` / `PageResult` instead of `*ResultDto`.
  - Message-oriented flows should remain explicit and separate.
- Key constraints:
  - Use Rider rename refactoring for symbol renames where possible.
  - Preserve current business behavior while changing naming and call paths.
  - Build and run targeted tests after edits.
- Non-goals:
  - Full architectural redesign beyond the already approved guideline changes.
  - Cross-BC integration redesign.

## Stages

### Stage 1
- Goal:
  - Inventory and classify rename targets by bounded context and entry style.
- Scope:
  - Product / Order / Inventory application, presentation, and related tests
- Non-goals:
  - Final code migration
- Risks:
  - Existing symbols may mix HTTP entry concerns and message-oriented concerns in the same file
- Recommended implementer:
  - `staged-refactor-implementer`

### Stage 2
- Goal:
  - Execute the implementation migration and update call sites.
- Scope:
  - Explicit use case types
  - controller invocation style
  - DI registration
  - tests
- Non-goals:
  - Non-essential style cleanup
- Risks:
  - Broad rename impact across controllers, tests, and Wolverine discovery
  - Some current handlers may need extraction rather than pure rename
- Recommended implementer:
  - `staged-refactor-implementer`

## Validation Strategy

- Reviewer checkpoints:
  - HTTP controllers no longer use `IMessageBus` as the default application boundary.
  - Use case naming follows the approved guideline.
  - Message-oriented handlers remain explicit where still needed.
- Tests/validation expectations:
  - Build the changed projects.
  - Run targeted tests for affected BCs where available.

## Notes

- Open questions:
  - None at workflow start; implementation decisions should follow the approved guideline set.
- Dependencies:
  - `.dev/standards/USECASE-COMMAND-HANDLER-RELATIONSHIP.MD`
  - `.dev/ARCHITECTURE.MD`
  - `.dev/standards/project-structure.md`
