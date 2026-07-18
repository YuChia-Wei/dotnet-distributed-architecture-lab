# Durable Backlog

This directory stores durable work items that must remain discoverable outside
any single workflow. It is not a second workflow engine.

## Ownership Boundary

- `INDEX.MD` owns the backlog catalog and current item state.
- `items/<item-id>.yaml` owns the problem, priority, origin, acceptance boundary,
  and workflow handoff for one durable item.
- `.dev/assessments/<assessment-id>/` owns durable observations and finding
  evidence that may be selected as backlog work.
- `.dev/workflows/<workflow-id>/` owns execution plans, tasks, evidence, and
  commits after work is scheduled.
- A workflow must link its source backlog item. The backlog item must link the
  active or completed workflow and be updated when the handoff state changes.

## States

`open -> planned -> in_progress -> resolved`

Use `declined` only with decision evidence. Do not duplicate task-level progress
in backlog items.

## Item Identity

- Preserve an existing finding or decision ID when one already exists.
- Otherwise use a stable uppercase path-safe ID such as `CTX-001`.
- Store one machine-readable YAML item per file under `items/`.
- Record full-date timestamps with an explicit UTC offset.
- Preserve `origin_refs`, `workflow_refs`, and `task_refs` so deferred findings
  remain traceable without copying workflow progress.
- Reference assessment findings as `<assessment-id>#<finding-id>` in
  `origin_refs`; do not copy the full assessment report into a backlog item.
