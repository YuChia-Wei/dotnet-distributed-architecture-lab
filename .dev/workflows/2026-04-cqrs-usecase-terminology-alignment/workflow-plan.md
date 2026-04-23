# Workflow Plan

## Metadata

- `plan_id`: `workflow-plan-2026-04-cqrs-usecase-terminology-alignment`
- `owner_skill`: `ddd-ca-hex-architect`
- `status`: `active`

## Context

- Problem statement:
  - The repository aims to stay aligned with CQRS + DDD + Clean Architecture + Hexagonal Architecture, but the current team has started to develop conflicting interpretations around `command`, `command handler`, `use case input DTO`, and `use case`.
  - The current repo rule that "handler can be the use case implementation" is directionally useful, but it has also blurred the distinction between the conceptual business operation and the concrete application-layer execution object.
- Current scope:
  - Clarify terminology and architectural boundaries for command-side application flow.
  - Compare repo-local definitions against externally grounded CQRS/DDD/CA/Hexagonal references.
  - Produce concrete guideline adjustments for stable team-wide usage.
- Why this workflow now:
  - New team members are already showing naming and conceptual conflicts.
  - If terminology remains unstable, future code and docs will drift in incompatible directions.

## Target Direction

- Target architecture summary:
  - Keep `use case` as the application/business operation boundary.
  - Keep `command` as an input message or request model for a state-changing operation.
  - Keep `command handler` as the application-layer executor for a command-driven entry path.
  - Define whether a separate `use case input DTO` should exist, when it should exist, and how it differs from a command.
  - Tighten guideline wording so CQRS, DDD, CA, and Hexagonal vocabulary remain compatible instead of becoming repo-local slang.
- Key constraints:
  - Cross-BC communication remains MQ-only.
  - Adjustments must be practical for the current repo structure and Wolverine-based dispatch.
  - Definitions should avoid unnecessary abstraction layers.
- Non-goals:
  - Full codebase refactor in this workflow.
  - Replacing Wolverine dispatch strategy.
  - Rewriting all BC implementations before terminology is settled.

## Stages

### Stage 1
- Goal:
  - Establish stable terminology using repo context plus primary CQRS/DDD/architecture references.
- Scope:
  - `command`
  - `command handler`
  - `use case`
  - possible `use case input DTO` / alternative naming
  - how these terms map onto in-process dispatch and adapter boundaries
- Non-goals:
  - Editing all existing code
  - Deciding every naming convention outside command-side flow
- Risks:
  - Overfitting to team-specific language
  - Reintroducing mediator/framework terms as architecture terms
- Recommended implementer:
  - `ddd-ca-hex-architect`

### Stage 2
- Goal:
  - Translate the agreed terminology into repo guideline changes.
- Scope:
  - `.dev/ARCHITECTURE.MD`
  - `.dev/standards/USECASE-COMMAND-HANDLER-RELATIONSHIP.MD`
  - `.dev/standards/project-structure.md`
  - related rationale docs for repositories and query-side layering
- Non-goals:
  - Full implementation migration across all BCs
  - Style-only document cleanup unrelated to terminology
- Risks:
  - Guidelines may become internally inconsistent if only partially updated
  - Existing examples may still conflict after rule changes
- Recommended implementer:
  - `ddd-ca-hex-architect`

## Validation Strategy

- Reviewer checkpoints:
  - Terminology is externally defensible, not only repo-local.
  - Each term has a distinct responsibility boundary.
  - The resulting guideline supports CQRS + DDD + CA + Hexagonal without forcing useless indirection.
- Tests/validation expectations:
  - No runtime tests required for the workflow setup artifact itself.
  - Later guideline changes should be reviewed for internal consistency against existing architecture docs and repo rules.

## Notes

- Open questions:
  - Should `command` always be the use case input DTO on the command side, or should the repo distinguish transport DTO from application input model more explicitly?
  - Should the repo standardize on `Use Case Request`, `Command`, or another term when the entry path is not bus-driven?
- Dependencies:
  - Primary repo guidance under `.dev/`
  - Externally grounded CQRS/DDD/CA/Hexagonal references to avoid biased terminology
