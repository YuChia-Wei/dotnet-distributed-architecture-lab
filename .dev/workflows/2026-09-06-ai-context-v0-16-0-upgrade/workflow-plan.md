# AI Collaboration Framework v0.16.0 Upgrade Workflow

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-09-06-ai-context-v0-16-0-upgrade`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `executing_skill`: `ai-context-upgrader`
- `branch`: `codex/2026-09-06-ai-context-v0-16-0-upgrade`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `completed`
- `current_phase`: `completed`
- `artifact_root`: `.dev/workflows/2026-09-06-ai-context-v0-16-0-upgrade`
- `created_at`: `2026-09-06T22:03:42+08:00`
- `updated_at`: `2026-09-06T23:21:20+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`
- `online_issue`: `YuChia-Wei/dotnet-distributed-architecture-lab#9`

## Objective And Scope

- Problem statement: the target has a validated v0.15.1 installation and v0.16.0 is now a stable published release with a declared direct route from v0.15.1.
- Authorized remediation scope: verify the public release package and direct edge, preserve all target-owned truth and selected components/providers, apply only an accepted source-specific plan, independently audit the resulting AI context, and finalize target provenance at v0.16.0.
- Exclusions: product `src/**` and `tests/**`; personal CLI routing data; source release mutation; push; pull request; merge; Issue closure; tags; GitHub Release mutation.
- Completion criteria: public ZIP and sidecar match hosted and admitted identities; incoming validation and route resolution pass; every operation is explicitly accepted or preserved; target-owned validation passes; the post-upgrade audit has no blocking finding; provenance, customizations, effective-rule state and packets are finalized; a local Git checkpoint passes repository policy.

## Version Identity And Compatibility Route

| Identity | Value | Status |
| --- | --- | --- |
| Installed source | `REL-v0.15.1`, tag `v0.15.1`, commit `f2b5fa7c13550efaeb65ab9fcaeb0403baa2a5af` | validated target baseline |
| Published Release | `REL-v0.16.0`, tag `v0.16.0`, peeled commit `f1ead6d676193ba24d8517aed08f05fcfa23cbd3` | stable, non-draft, non-prerelease |
| Admitted package source | `ai-collaboration-framework-v0.16.0`, build commit `4d1a5c7d039618f007784679d9968c357347272b` | package and route authority |
| Public ZIP | SHA-256 `d136b69e4153e7c85f892871fb0d3e6c5d8f88c7fd89d43fdb1b03ca88c5c85d` | GitHub, sidecar and admission match |
| Selected edge | `v0.15.1-to-v0.16.0-direct` | `route_kind: direct`, no diagnostics |

The source release contract explicitly permits the public body to bind the final tag commit while the unchanged archive retains its preparation-commit provenance. Target provenance therefore follows the admitted package and route authority commit; the workflow retains both identities rather than conflating them.

## Semantic Customization Reconciliation

| Customization | Subject | Incoming focus | Proposed disposition | Decision basis |
| --- | --- | --- | --- | --- |
| `CUST-DOTNET-MQ-GOVERNANCE` | `rule:downstream-ai-context-governance-projection` | retired aliases, diagnostic routing, root collaboration and Issue binding | merge | preserve Issue-first and target routing while adopting compatible v0.16 framework behavior |
| `CUST-DOTNET-MQ-VALIDATION` | `contract:downstream-validation-runtime` | content-addressed evidence reuse, dependency observation, target validation and packet layout | merge | preserve the target SHA-pinned gate and only adopt compatible framework mechanics |
| `CUST-DOTNET-MQ-REPO-TRUTH` | `contract:target-repository-truth-boundary` | project naming, product facts and target-owned indexes | retain | repository-native target truth remains authoritative |
| `CUST-DOTNET-MQ-EXECUTION-PROVENANCE-ADOPTION` | `rule:target-execution-provenance-adoption-boundary` | commit grammar and execution provenance | merge | preserve the existing prospective cutover and exact legacy waiver |

The first no-write package plan contained 70 automatic operations (47 replacements, 17 additions and 6 removals), with no package-level reconciliation, ignored path or managed-state conflict. Target reconciliation is still required outside those framework-managed operations: the routine validation profile must point to this active workflow, and current target entry documents must route to `software-development-orchestrator` and `ai-context-init` before the old wrapper files are removed. Those target-owned changes are checkpointed before regenerating the sealed plan.

## Stages And Checkpoints

1. Bind Issue #9, preserve the clean starting commit, validate the hosted release assets, incoming payload and direct route.
2. Generate the exact v0.15.1-source package plan and remediation packet outside the target; classify operations and reconcile target-owned semantics.
3. Seal the owner decision and durable package-apply transaction, apply accepted operations, and preserve rollback until target validation passes.
4. Execute the target-owned validation route and retain its receipt; perform a separate read-only post-upgrade audit.
5. Finalize target authorities, validate the terminal receipt and exact target gate, update workflow evidence, and create a local checkpoint.

## Rollback Boundary

- Starting commit: `f1a0298fdca0dafe1d653802006e60bc004a74a5` on clean `main`, equal to `origin/main` at branch creation.
- Plan, remediation packet and decision stay outside tracked target paths until the package tool seals the Git-admin transaction.
- Before finalization, recovery uses the exact extracted package with `--resume`, or Git-admin prestates with `--rollback`; neither path changes authority.
- After a valid terminal receipt finalizes provenance, transaction rollback is forbidden; the local workflow checkpoint becomes the repository recovery boundary.

## Resume Checkpoint

- Last completed action: finalized transaction `48d34abf53d7e8fc37bb8b51a9e3f128cac8954b62b71da1d094158d74255f22`, fixed the applied audit subject at `c0abe9c2ce288abf2b83edce1806fefb63b5886e`, persisted `ASM-20260906-001`, cleared the verified transient receipt, and passed the journal-only final target gate.
- Current task: none; `AICU-001`, `AICU-002`, and `AICU-003` are complete.
- Exact next action: none within the authorized local scope. Push, pull request, merge, Issue closure, and publication require separate authorization.
- Validation completed: public Release and ZIP identity; package validation (`650` files, `18` portable entrypoints); direct route resolution; 70/70 operations; target-validation receipt; terminal receipt; 13 effective rules; 20 route packets; 15/15/15 skill parity; 16 assessment artifacts; 34/34 target tests; final commit-policy range.
- Git state: applied checkpoint `c0abe9c2ce288abf2b83edce1806fefb63b5886e`; the workflow closeout commit contains this completed plan and reports.
- Branch history and checkpoint handoffs: segment 1 only; no push or merge handoff.
- Blockers or unresolved decisions: none for local completion. Audit findings `ASM-20260906-001#AIC-001` through `#AIC-005` remain upstream operability follow-ups.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-09-06-ai-context-v0-16-0-upgrade` | `main` | workflow-start | `f1a0298fdca0dafe1d653802006e60bc004a74a5` | local | `2026-09-06T22:03:42+08:00` | Issue #9 authorizes the governed v0.15.1-to-v0.16.0 upgrade | Continue on the same branch with package planning |
| 1 | `codex/2026-09-06-ai-context-v0-16-0-upgrade` | `main` | finalized-audit-subject | `c0abe9c2ce288abf2b83edce1806fefb63b5886e` | local | `2026-09-06T23:13:50+08:00` | Preserve finalized v0.16.0 authorities while excluding the transient pending receipt from durable target history | Complete local closeout on the same branch |
