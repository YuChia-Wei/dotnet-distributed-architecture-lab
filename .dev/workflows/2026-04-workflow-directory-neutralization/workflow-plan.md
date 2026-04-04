# Workflow Directory Neutralization Plan

## Purpose

Rename the workflow artifact root from `refactor-workflows` to `workflows` and rename per-workflow `refactor-plan.md` to `workflow-plan.md` so the structure reflects generic workflow records rather than only refactoring work.

## Nature

- Knowledge-base structure refactor
- Workflow artifact contract neutralization
- Path and naming normalization

## Scope

- `.dev/workflows/` directory and all child workflow folders
- All repo references to `.dev/workflows/`
- All repo references to `workflow-plan.md`
- Workflow guide and portability documentation

## Non-Goals

- Moving workflow artifacts out of `.dev/`
- Changing the task JSON model
- Renaming `review-report.md` or `tasks/`

## Stages

1. Define the neutralized workflow contract and record this workflow.
2. Rename directory and plan filenames to `workflows/` and `workflow-plan.md`.
3. Update repo references and historical workflow records to the new paths.
4. Validate the renamed structure and close the workflow.

## Risks

- Missing path references in historical artifacts
- Leaving mixed terminology between `refactor-workflows` and `workflows`
- Creating a workflow that cannot describe itself after the rename

## Success Criteria

- `.dev/workflows/` is the only active workflow artifact root.
- `workflow-plan.md` is the only active per-workflow plan filename.
- High-traffic guides and AGENTS instructions point only to the new structure.

## Placement Decision

- Keep `workflows/` under `.dev/` for now.
- Treat it as project knowledge governance, not as a repo-root operational system.
- Revisit a root-level move only if workflow records later become a separate repo-wide governance surface.


