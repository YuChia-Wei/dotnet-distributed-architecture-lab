# AI Collaboration Framework v0.15.1 Upgrade Workflow

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-08-30-ai-context-v0-15-1-upgrade`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-08-30-ai-context-v0-15-1-upgrade`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `in_progress`
- `current_phase`: `blocked-remediation-recovery`
- `artifact_root`: `.dev/workflows/2026-08-30-ai-context-v0-15-1-upgrade`
- `created_at`: `2026-08-30T18:16:45+08:00`
- `updated_at`: `2026-08-30T20:30:39+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`
- `online_issue`: `YuChia-Wei/dotnet-distributed-architecture-lab#3`

## Objective And Scope

- Problem statement: the target has a validator-ready v0.13.0 installation, while the requested v0.15.1 package supports automatic upgrade only from v0.15.0.
- Authorized remediation scope: first prove whether v0.13.0 can directly upgrade to v0.15.1, then use only published package identities and supported edges to reach v0.15.1 while preserving target-owned truth and semantic customizations.
- Exclusions: product `src/**` and `tests/**`; source release records; publication; push; pull request; merge; Issue closure; tags; GitHub Release mutation.
- Completion criteria: each archive and sidecar matches; every selected edge passes package planning and apply validation; target-owned files are reconciled explicitly; independent post-upgrade audit and target validation pass; provenance, customizations, effective-rule state, and packets describe v0.15.1; local workflow commits pass repository policy.

## Version Identity And Compatibility Route

| Edge | Package | Published commit | Planner status |
| --- | --- | --- | --- |
| v0.13.0 to v0.15.1 | `ai-collaboration-framework-v0.15.1` | `f2b5fa7c13550efaeb65ab9fcaeb0403baa2a5af` | rejected: source manifest is not supported |
| v0.13.0 to v0.14.0 | `ai-context-dotnet-backend-v0.14.0` | `412bb14a16fe75ee65a020b16680def0acc0ff1b` | supported; reconciliation required |
| v0.14.0 to v0.15.0 | `ai-collaboration-framework-v0.15.0` | `5fedaceef7e18b4cdcde3cb665adcc97070db2df` | immediate-predecessor edge; verify after v0.14.0 checkpoint |
| v0.15.0 to v0.15.1 | `ai-collaboration-framework-v0.15.1` | `f2b5fa7c13550efaeb65ab9fcaeb0403baa2a5af` | immediate-predecessor edge; verify after v0.15.0 checkpoint |

## Semantic Customization Reconciliation

| Customization | Subject | Incoming focus | Proposed disposition | Evidence |
| --- | --- | --- | --- | --- |
| `CUST-DOTNET-MQ-GOVERNANCE` | `rule:downstream-ai-context-governance-projection` | root collaboration, Issue binding, runtime agent profiles | merge | existing approved ledger decision and Issue #3 |
| `CUST-DOTNET-MQ-VALIDATION` | `contract:downstream-validation-runtime` | package planner, target validator, cache/runtime identity | merge | existing approved ledger decision and exact package receipts |
| `CUST-DOTNET-MQ-REPO-TRUTH` | `contract:target-repository-truth-boundary` | target README, specifications, problem frames, root identity | retain | repository-native target truth and three-way diffs |
| `CUST-DOTNET-MQ-EXECUTION-PROVENANCE-ADOPTION` | `rule:target-execution-provenance-adoption-boundary` | prospective commit and execution provenance | merge | existing approved ledger decision and target commit gate |

## Reconciliation Decisions For v0.14.0

- Narrow `.gitignore` to ignore only root `.codex/*.toml`; keep `.codex/agents/**` and `.codex/skills/**` visible without negation rules so the package planner does not misclassify selected framework-managed paths as ignored.
- Preserve target semantics in `.editorconfig`, `.github/pull_request_template.md`, and `AGENTS.md`; merge only compatible incoming governance requirements.
- Keep target problem-frame and spec truth in the target-template `INDEX` files, where the current catalogs already enumerate every active target artifact. Restore the two unchanged framework-managed README files to their exact released bytes so every supported edge and finalization gate can verify the managed-path identity.
- Keep `repo-backlog` enabled because provenance records target-owned preservation.
- Bind the target validation profile to `python -B .dev/ai-context/tooling/validate-target-ai-context.py --allow-unfinalized --workflow-id 2026-08-30-ai-context-v0-15-1-upgrade`; preserve `local.mode: manual` and `ci.mode: unconfigured`. The owner explicitly approved this executable profile after the v0.14 finalization preflight found that an empty `validation.routine.argv` could not produce a terminal target-validation receipt.

## Stages And Checkpoints

1. Verify Issue #3, current target authority, releases, archives, sidecars, and direct-jump rejection.
2. Apply and reconcile v0.13.0 to v0.14.0 from its exact manifest and retain receipt evidence.
3. Apply v0.14.0 to v0.15.0, preserving the public package identity cutover boundary.
4. Apply v0.15.0 to v0.15.1 and regenerate validation evidence under the stronger runtime fingerprint and finite timeout contract.
5. Run target validation and an independent `ai-context-auditor` post-upgrade assessment.
6. Finalize target authorities, workflow evidence, and local commits without external integration actions.

## v0.15.x Update-Cost Gate

- v0.14 applied 188 automatic operations and took approximately 87 minutes on
  Windows. Its engine rewrites the full journal and rescans the recovery surface
  after each operation.
- v0.15.0 declares 50 operations and replaces per-operation full-journal
  snapshots with append-only digest-chained progress records plus cached Git
  inspection.
- v0.15.1 declares 6 operations and carries the byte-identical apply engine used
  by v0.15.0.
- Static admission is therefore `PASS-FOR-MEASURED-DRY-RUN`; no later apply may
  start until the v0.14 finalization blocker is safely resolved.
- The retained post-apply unrelated-change guard still cannot distinguish
  required digest-bound target remediation from unrelated drift. This lifecycle
  defect requires separate tracking even though the main performance mechanism
  is materially improved.

## Rollback Boundary

- Starting commit: `cedd590e4f3393b5cb3ad5a0be5f5663274bb584` on clean `main`, equal to `origin/main` after fetch.
- Every apply must use a fresh digest-bound plan and retain its transaction receipt.
- A failed edge keeps the last successfully validated provenance and blocks the next edge.
- Git commits provide durable checkpoints; destructive reset and history rewrite are not authorized.

## Resume Checkpoint

- Last completed action: v0.14 applied all 188 automatic operations; target remediation and `ASM-20260830-001` were validated; the exact target gate passed; and the v0.15.x static performance preflight confirmed append-only progress with only 50 and 6 declared operations.
- Current task: `AICU-001-supported-route-upgrade`.
- Exact next action: obtain an owner decision before preserving the remediation patch, rolling back the unfinished v0.14 transaction, committing target validation preconditions, and regenerating the sealed v0.14 plan for a clean reapply.
- Validation already completed: package identities and sidecars; direct-jump fail-closed result; 188-operation v0.14 apply; 33 target-owned tests; exact pre-finalization target gate; assessment and workflow validators; v0.15.x static operation and engine comparison.
- Git state: dedicated local workflow branch at transaction-start commit `32140f52ffffd14dc235b310d386d6c1b3765e70`, with the v0.14 package delta, target remediation, assessment, and reports uncommitted under an unfinished transaction.
- Branch history and checkpoint handoffs: segment 1 only; no push or merge handoff.
- Blockers or unresolved decisions: the v0.14 recorder rejects the target-owned remediation required by its own target validation contract. Rollback and reapply may repeat substantial v0.14 cost and therefore requires explicit owner approval. Detailed public follow-up Issue creation also requires explicit approval.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-30-ai-context-v0-15-1-upgrade` | `main` | workflow-start | `cedd590e4f3393b5cb3ad5a0be5f5663274bb584` | local | `2026-08-30T18:16:45+08:00` | Issue #3 authorized the governed upgrade and direct-jump analysis | Continue on the same branch with v0.14.0 planning and apply |
