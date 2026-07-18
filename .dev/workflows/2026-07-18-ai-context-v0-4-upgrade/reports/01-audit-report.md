# AI Context Upgrade Baseline

## Report Metadata

- `report_id`: `upgrade-baseline-2026-07-18-ai-context-v0-4-upgrade`
- `workflow_id`: `2026-07-18-ai-context-v0-4-upgrade`
- `owner_skill`: `ai-context-governance`
- `status`: `final`
- `created_at`: `2026-07-18T20:33:26+08:00`
- `updated_at`: `2026-07-18T20:40:48+08:00`

## Evidence Used

- Target branch and clean worktree at `main` commit `d3d7f18`.
- Completed target workflow `2026-07-15-ai-context-v0-1-downstream-feedback`.
- Source immutable tags and published release registry in `C:\Github\YuChia\ai-collaboration-prompts-dotnet-backend`.
- `REL-v0.1.0`, `REL-v0.2.0`, `REL-v0.3.0`, and `REL-v0.4.0` release and migration contracts.
- Incoming `ai-context-upgrader` version policy, three-way boundaries, provenance contract, and output contract.
- Locally reproduced v0.3.0 and v0.4.0 governed packages built from immutable tags with the v0.4.0 tagged package tool.
- Package validator output for both archives and the v0.3.0 dry-run plan covering 555 distributable paths.

## Baseline Findings

| Finding | Evidence | Consequence |
| --- | --- | --- |
| `AICUP-BASELINE` | Target retained durable evidence that its import derives from source `v0.1.0` at `69c285077708dfb96ee49bb39258aec83eb7f1a9`, but predates `.dev/AI-CONTEXT-SOURCE.yaml`. | Treat the base as known historical identity with manual file-selection reconciliation; do not infer package ownership. |
| `AICUP-V03` | `REL-v0.3.0` lists v0.1.0 as a reconciliation source and no automatic upgrade sources. | Account for v0.2.0 breaking contracts and review every package operation before applying v0.3.0. |
| `AICUP-V04` | Published `REL-v0.4.0` supports only governed v0.3.0 and declares no automatic upgrade sources. | Validate and record the intermediate v0.3.0 state before using its `files.yaml` as the v0.4.0 planner base. |
| `AICUP-TARGET-TRUTH` | Root collaboration entries, project knowledge, workflow catalogs, local validators, and repository structure are target-owned or locally changed. | Preserve these paths unless semantic reconciliation proves an incoming framework update is appropriate. |

## v0.3.0 Three-Way Classification

| Classification | Count | Decision |
| --- | ---: | --- |
| Target bytes equal v0.1.0 base | 433 | Safe framework replacement candidate; apply v0.3.0 bytes. |
| Incoming path absent in target | 49 | Safe add candidate, subject to package ownership and exclusion rules. |
| Target already equals v0.3.0 | 4 | Keep unchanged. |
| Target changed from v0.1.0 | 68 | Three-way reconcile; preserve target-owned downstream corrections and merge incoming framework contracts. |
| Target path has no v0.1.0 base | 1 | Preserve the target exact-case regression test and evaluate it as a local override. |

Of the 68 changed paths, 56 are packaged as `framework-managed` and 12 as `target-template`. Existing downstream workflow evidence establishes that many of these changes intentionally repaired target identity, workflow governance, exact-case links, and wrapper routing. Path ownership and content must therefore be re-read during application rather than inferred from the package profile alone.

## Initial Verdict

`ready-to-apply`: source identities, rollback boundary, package integrity, and all v0.3.0 incoming paths are classified. The user explicitly authorized the upgrade. Apply only the 482 safe replacement/add candidates directly; three-way reconcile the 68 changed paths and preserve the one target-only regression test.
