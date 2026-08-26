# Durable Backlog

This directory stores durable work items that must remain discoverable outside
any single workflow. It is not a second workflow engine.

## Ownership Boundary

- `INDEX.MD` owns the backlog catalog and current item state.
- `ROADMAP.md` owns the active cross-release horizon, release-level state,
  activation gates, and workflow handoffs. It does not duplicate child workflow
  tasks or validation evidence.
- `plans/` preserves durable source plans that informed the roadmap. Those
  sources are not assessment artifacts and do not own live release state.
- `items/<item-id>.yaml` owns the problem, priority, origin, acceptance boundary,
  and workflow handoff for one durable item.
- `.dev/assessments/<assessment-id>/` owns durable observations and finding
  evidence that may be selected as backlog work.
- `.dev/workflows/<workflow-id>/` owns execution plans, tasks, evidence, and
  commits after work is scheduled.
- When the selected work-item binding mode requires or uses a backlog item, the
  workflow must link it and the item must link the active or completed workflow.
  The selected provider contract owns that mode and merge-reference rule. This
  source repository records `required` in its source-only provider
  configuration; downstream targets must select their own binding mode rather
  than inheriting it from this portable guide. Provider state alone never
  authorizes work.

This directory catalogues the local durable backlog, not the complete online
GitHub Issue queue or Project #3. Current provider counts, field options, and
bounded read-back evidence belong in `providers/github.yaml` and
`provider-mappings/`; do not infer online completeness from the number of local
item YAML files.

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

## Release Metadata

Every backlog item records:

```yaml
release:
  target: "v0.5.0"   # or "unassigned"
  completed_in: null # set when the item reaches resolved
  published_in: null # set to the first release tag containing the resolution
```

- `target` is the release expected to complete the item's declared scope. Use
  `unassigned` instead of guessing.
- `completed_in` identifies the release train that accepted the completed work.
- `published_in` identifies the first immutable published version containing the
  resolution. It may remain `null` between completion and publication.
- A resolved item must set `completed_in`.
- For governed releases from v0.7.0 onward, all resolved items whose
  `completed_in` equals the version form that version's canonical included-work
  set. Candidate `release.yaml.planning.backlog_refs` must equal that complete
  set, with each item listed exactly once. A target assignment without resolved
  completion is not included work.
- When `published_in` is set, preserve Git ancestry evidence in the item when
  available.
- Roadmap-level horizons remain in `ROADMAP.md`; do not create a synthetic
  backlog item merely to represent the roadmap.
