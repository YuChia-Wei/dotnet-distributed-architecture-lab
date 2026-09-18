# AI Collaboration Framework v0.18.0 Trial Workflow

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-09-18-ai-context-v0-18-0-trial`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-09-18-v018-trial-03`
- `base_branch`: `main`
- `status`: `in_progress`
- `current_phase`: `preapply-target-projection-correction`
- `artifact_root`: `.dev/workflows/2026-09-18-ai-context-v0-18-0-trial`
- `created_at`: `2026-09-18T07:53:09+08:00`
- `updated_at`: `2026-09-18T08:05:37+08:00`
- `online_issue`: `YuChia-Wei/dotnet-distributed-architecture-lab#12`

## Scope And Baseline

This workflow prepares target-owned gate reconciliation for a user-authorized,
ephemeral v0.18.0 trial. The original preapply target baseline is commit
`4507aecb7f2132abf7ec7f1b41aabc7f1aa35ed5`; the bounded projection-correction
checkout is commit `aac22bd892aec0edd6ef6ae4a7451790fe0548cb` on
`codex/2026-09-18-v018-trial-03`. It does not apply a package, change
provenance, customizations, effective rules or packets, finalize a transaction,
or claim adoption or release readiness.

The completed v0.16.0 workflow retains its immutable audit record unchanged.
That record verifies the authority bytes in its reviewed Git subject only and
is explicitly not current-HEAD admission. This v0.18.0 workflow has no
terminal-audit contract or terminal receipt yet.

## Incoming Package Rebind Point

The following candidate08 identity is the package-validated preapply input and must remain
bound as one unit before a package plan is sealed:

| Input | Candidate08 value |
| --- | --- |
| Framework version | `v0.18.0` |
| Package source commit | `eaba751b71872e085f8ffd1b8a0fbbefa554f379` |
| ZIP SHA-256 | `3a8f7d753b0f45dde2e9f77e43b3f7dbc87f8fb69c1231b2d2463245c1e4d5d2` |
| Portable / source-only / missing source-only entrypoints | `20 / 25 / 25` |

A replacement candidate must update only the incoming identity projections:
`target-gate-manifest.yaml` top-level `framework_commit`,
`AICU-V016-TARGET-GATE-PROJECTION-001.framework_commit`, its generic-validator
and Python-entrypoint digests, this table, and the static commit assertion in
`test_downstream_package_projection.py`. The v0.18.0 version and the
20/25/25 applicability boundary remain subject to exact package verification.

## Current Task

- `AICU-001-preapply-gate-reconciliation` remains in progress while the target-owned role-path projection test is corrected and the root seals the canonical package plan.

## Current Target-Suite Evidence

Candidate08 target validation ran 55 tests: 53 passed and exactly two failed:
`test_gwt_005_review_roles_do_not_require_shared_rule_bundles` and
`test_gwt_007_route_reference_graph_is_smaller_than_baseline`. Both loaded
hard-coded shared code-review role paths that candidate08 relocates into the
owning `code-reviewer` skill. No passing receipt exists. The correction derives
these four paths from the installed skill's `role_bindings` by stable
`role_asset_id`; it does not change role semantics, rule bundles, or reference-graph assertions. The focused seven-test projection suite and candidate08 static closure now pass; this does not replace the failed 55-test run or create a receipt.

## Required Next Actions

1. Rebind the frozen package identity and rebuild target-owned effective-state
   artifacts before committing the preapply reconciliation.
2. Generate and validate the canonical package plan, then apply only its
   accepted operations.
3. Run the selected target-owned validation after the applied bytes are fixed.
4. Obtain a separate independent audit of the canonical content subject and an
   actual terminal receipt. Finalization remains pending until both are
   validated against the applied target.

No historical receipt is repurposed for the v0.18.0 trial, and no pending
receipt is recorded as passed evidence.
