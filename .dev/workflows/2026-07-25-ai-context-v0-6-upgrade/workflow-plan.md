# AI Context v0.6.0 Upgrade

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-07-25-ai-context-v0-6-upgrade`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `execution_skill`: `ai-context-upgrader`
- `branch`: `codex/2026-07-25-ai-context-v0-6-upgrade`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `in_progress`
- `current_phase`: `remediation-planning`
- `artifact_root`: `.dev/workflows/2026-07-25-ai-context-v0-6-upgrade`
- `created_at`: `2026-07-25T07:05:01+08:00`
- `updated_at`: `2026-07-25T07:05:01+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: the target is validated at `REL-v0.4.0`, while the requested published release is `REL-v0.6.0`; v0.6.0 accepts only exact v0.5.0 provenance.
- Authorized remediation scope: execute the governed automatic v0.4.0-to-v0.5.0 package route, validate and checkpoint provenance, then execute the governed v0.5.0-to-v0.6.0 route while preserving target-owned truth and declared local overrides.
- Exclusions: do not import source workflows, assessments, backlog instances, release history, product source, product tests, source Git metadata, or source-only publication tooling; do not overwrite root collaboration, requirements, specs, ADRs, architecture, operations, project configuration, or repository catalogs without reconciliation.
- Completion criteria: published tag identities and package manifests validate; both stages apply from clean committed checkpoints; target-required validation passes after each stage; v0.6.0 provenance and semantic customization authority are finalized without unresolved reconciliation; workflow evidence and commits close cleanly.

## Version Identity

| Stage | From | From Commit | To | To Commit | Contract |
| --- | --- | --- | --- | --- | --- |
| 1 | `REL-v0.4.0` | `5af1db672928f9d51f55fee04183ad27b79fb9f8` | `REL-v0.5.0` | `1477181f0b43fa7ee82fcd482141758ac9e22eb6` | migration schema 2.0.0; exact v0.4.0 source supported |
| 2 | `REL-v0.5.0` | `1477181f0b43fa7ee82fcd482141758ac9e22eb6` | `REL-v0.6.0` | `8b98b5f917513f2d143f42a322050a1162bb63f9` | migration schema 3.0.0; exact v0.5.0 source required |

## Upgrade Safety

- Rollback boundary: clean `main@2eeddf392ca79deb4407c47d13ad53178015ba90`.
- Stage 1 checkpoint must be committed before planning stage 2.
- Package archives are built from immutable annotated tags outside the target and validated before use.
- Reconciliation acknowledgement preserves the target path; it never authorizes overwrite or deletion.
- Target-owned paths and all declared overrides are manually reconciled after each package apply.
- Provenance is updated only after the corresponding stage validation succeeds.

## Task Plan

| Task | Purpose | Status |
| --- | --- | --- |
| `AICUP6-001` | Validate releases, build immutable packages, classify v0.4.0-to-v0.5.0 changes, and persist the apply plan. | `in_progress` |
| `AICUP6-002` | Apply and reconcile v0.5.0, validate, update provenance, and commit the intermediate checkpoint. | `pending` |
| `AICUP6-003` | Plan, apply, and reconcile v0.6.0 including component selection, new provenance authority, and semantic customization ledger. | `pending` |
| `AICUP6-004` | Run final repository validation, reconcile workflow evidence, commit closeout, and report remaining overrides. | `pending` |

## Resume Checkpoint

- Last completed action: verified target v0.4.0 provenance and immutable source release identities; confirmed the required v0.4.0-to-v0.5.0-to-v0.6.0 route; read every intervening migration guide.
- Current task: `AICUP6-001`.
- Exact next action: build v0.4.0 and v0.5.0 package envelopes from immutable tags, validate them, run the v0.5.0 planner against the clean target, and persist the full classification.
- Validation already completed: target worktree clean and synchronized with origin; source main clean; tag peeled commits match the published release registry; read-only Git three-way discovery found 81 automatic candidates, 63 reconciliation paths, and 171 source-only exclusions for v0.4.0-to-v0.5.0.
- Git state: workflow branch created from `main@2eeddf392ca79deb4407c47d13ad53178015ba90`; no framework path has been applied.
- Branch history and checkpoint handoffs: segment 1 started locally; no push or merge requested.
- Blockers or unresolved decisions: none. The user authorized the requested upgrade; target-owned reconciliation defaults to preservation.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-07-25-ai-context-v0-6-upgrade` | `main@2eeddf392ca79deb4407c47d13ad53178015ba90` | started | pending | local | `2026-07-25T07:05:01+08:00` | Execute the authorized progressive upgrade with explicit stage checkpoints. | Continue `AICUP6-001`. |
