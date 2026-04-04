# Workflow Directory Neutralization Closure

## Outcome

This workflow completed the neutralization of the workflow artifact contract.

## Completed Changes

1. Renamed `.dev/refactor-workflows/` to `.dev/workflows/`
2. Renamed per-workflow `refactor-plan.md` to `workflow-plan.md`
3. Updated repo-wide references in AGENTS, guides, README files, portability documents, and historical workflow records
4. Added an explicit location rule that keeps `workflows/` under `.dev/` for now

## Final Contract

```text
.dev/workflows/
  <workflow-id>/
    workflow-plan.md
    review-report.md
    tasks/
      <task-id>.json
```

## Decision

- Keep the workflow artifact root under `.dev/`
- Treat it as part of the project knowledge system rather than a repo-root operational surface
- Re-evaluate a root-level move only if a future repo-wide workflow system emerges
