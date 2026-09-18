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
- `branch`: `codex/2026-09-18-v018-trial-04`
- `base_branch`: `main`
- `status`: `in_progress`
- `current_phase`: `preapply-selector-discovery-and-source-identity-rebind`
- `artifact_root`: `.dev/workflows/2026-09-18-ai-context-v0-18-0-trial`
- `created_at`: `2026-09-18T07:53:09+08:00`
- `updated_at`: `2026-09-18T08:49:09+08:00`
- `online_issue`: `YuChia-Wei/dotnet-distributed-architecture-lab#12`

## Scope And Checkpoint

This workflow prepares a user-authorized, ephemeral v0.18.0 target trial. The
fresh isolated checkpoint is commit
`6d91126670a4702d1831636b5892e637e5d8431f` on
`codex/2026-09-18-v018-trial-04`. It is a preapply checkpoint: it does not
apply a package, change provenance, customizations, effective rules or packets,
finalize a transaction, or claim adoption or release readiness.

Candidate08 source-package finalization succeeded. A prior pre-finalization
55-test target run retained two errors; it is historical non-passing evidence,
and no individual pass count is inferred from that aggregate. Candidate09 ZIP
and tar package validation passed. Its exact source identity is now pinned as
`d3364303d55d1f3b8e67c720b04c1d3b34b1d4f3` while candidate08 evidence remains historical only. This
checkpoint does not project either candidate into a target transaction. No
rebind, plan, or apply operation has run.

The completed v0.16.0 workflow retains its immutable audit record unchanged.
That record verifies authority bytes in its reviewed Git subject only and is not
current-HEAD admission. This v0.18.0 workflow has no terminal-audit contract or
terminal receipt.

## Preserved Incoming Identity

| Input | Current manifest value |
| --- | --- |
| Framework version | `v0.18.0` |
| Framework commit | `d3364303d55d1f3b8e67c720b04c1d3b34b1d4f3` |
| Candidate08 ZIP SHA-256 (historical) | `3a8f7d753b0f45dde2e9f77e43b3f7dbc87f8fb69c1231b2d2463245c1e4d5d2` |
| Candidate09 ZIP/tar | Built and package-validated; ZIP SHA-256 `764eb3197b0ab76efaea1ca272e76fe7c9b780db348b60ab2b1bd3b7ccefd811`. |
| Portable / source-only / missing source-only entrypoints | `20 / 25 / 25` |

The parent supplied the corrected source commit and verified archive identity above. Git confirms that the
generic validator, Python entrypoint registry, and shell-assets blobs are unchanged
from candidate08, so their manifest hashes, counts, and defect declarations remain
unchanged. No customization, authority, effective-state, or packet bytes are changed
by this metadata checkpoint.

## Selector-Discovery Observations

Two independent model trials stopped before catalog verification because each
guessed an unavailable selector:

| Trial | Guessed selector | Result |
| --- | --- | --- |
| Terra candidate01 | `code-reviewer/review/csharp` | Invalid target selector; stopped before catalog checks. |
| Luna candidate01 | `code-review/direct/dotnet-backend/cs` | Invalid target selector; stopped before catalog checks. |

The ready target routes are `review/direct/csharp-review` and
`dotnet-mixed-review`. This checkpoint records the discovery failure without
selecting either route. The repaired source package must provide canonical
capability restoration and target selector-discovery guidance; the target will
resolve the applicable selector from that guidance when a separately authorized
operation consumes the corrected identity. Both model outputs remain retained as
non-passing observations. Neither creates a receipt, validates the target suite,
or establishes a cost saving.

## Current Task

- `AICU-001-preapply-gate-reconciliation` remains in progress. Candidate09 source
  identity is pinned; parent validation and commit of this checkpoint come next.
- The metadata work unit did not select or validate a review route. Existing
  target selectors remain unchanged; actual corrected model consumption is a
  separate usability acceptance after the new candidate is installed.

## Required Next Actions

1. Validate and commit this preapply checkpoint.
2. Under the existing owner authorization, create and validate the fresh canonical
   plan, review its prospective authority decision, and apply candidate09.
3. Bind the actual target-validation receipt, independently audit the immutable
   content projection, then canonically finalize and archive the terminal receipt.
4. Run the same bounded Terra/Luna task using exact target selector discovery.

Historical receipts and limited model observations remain evidence of their own
subjects and do not replace the new transaction's gates.
