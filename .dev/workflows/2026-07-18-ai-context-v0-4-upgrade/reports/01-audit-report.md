# AI Context Upgrade Baseline

## Report Metadata

- `report_id`: `upgrade-baseline-2026-07-18-ai-context-v0-4-upgrade`
- `workflow_id`: `2026-07-18-ai-context-v0-4-upgrade`
- `owner_skill`: `ai-context-governance`
- `status`: `draft`
- `created_at`: `2026-07-18T20:33:26+08:00`
- `updated_at`: `2026-07-18T20:33:26+08:00`

## Evidence Used

- Target branch and clean worktree at `main` commit `d3d7f18`.
- Completed target workflow `2026-07-15-ai-context-v0-1-downstream-feedback`.
- Source immutable tags and published release registry in `C:\Github\YuChia\ai-collaboration-prompts-dotnet-backend`.
- `REL-v0.1.0`, `REL-v0.2.0`, `REL-v0.3.0`, and `REL-v0.4.0` release and migration contracts.
- Incoming `ai-context-upgrader` version policy, three-way boundaries, provenance contract, and output contract.

## Baseline Findings

| Finding | Evidence | Consequence |
| --- | --- | --- |
| `AICUP-BASELINE` | Target retained durable evidence that its import derives from source `v0.1.0` at `69c285077708dfb96ee49bb39258aec83eb7f1a9`, but predates `.dev/AI-CONTEXT-SOURCE.yaml`. | Treat the base as known historical identity with manual file-selection reconciliation; do not infer package ownership. |
| `AICUP-V03` | `REL-v0.3.0` lists v0.1.0 as a reconciliation source and no automatic upgrade sources. | Account for v0.2.0 breaking contracts and review every package operation before applying v0.3.0. |
| `AICUP-V04` | Published `REL-v0.4.0` supports only governed v0.3.0 and declares no automatic upgrade sources. | Validate and record the intermediate v0.3.0 state before using its `files.yaml` as the v0.4.0 planner base. |
| `AICUP-TARGET-TRUTH` | Root collaboration entries, project knowledge, workflow catalogs, local validators, and repository structure are target-owned or locally changed. | Preserve these paths unless semantic reconciliation proves an incoming framework update is appropriate. |

## Initial Verdict

`ready-to-plan`: source identities and rollback boundary are available, the user explicitly authorized the upgrade, and the required progressive path is `v0.1.0` manual reconciliation → governed `v0.3.0` → published `v0.4.0`. No package application is safe until immutable packages are validated and all dry-run reconciliation items are classified.
