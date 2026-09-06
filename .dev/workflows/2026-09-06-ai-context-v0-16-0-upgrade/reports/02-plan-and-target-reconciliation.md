# v0.16.0 Plan And Target Reconciliation

## No-Write Package Plan

- Plan SHA-256: `8c6b3ee89807f50d21c3c08f51cb1497e41e7db039f0d02c71d6667e04cc85ec`.
- Observed starting commit: `9ae814e7136c6644350b260dc49853744cb9b21c`.
- Observed prestate SHA-256: `0bd77aa71760bec4f85fdde36df200dbf31df7b136df273c40c54248372cd180`.
- Operations: 70 total; 47 replacements, 17 additions and 6 removals.
- Component counts: 50 `software-development-core`, 20 `ai-context-lifecycle-core`.
- Package reconciliation IDs: none.
- Ignored framework-managed paths: none.
- Managed-state conflicts: none.
- Selection preserved: mandatory core components, `dotnet-backend`, and enabled `repo-backlog`.

This first plan is discovery evidence only. It is intentionally invalidated by the target-owned reconciliation below and will not be applied or reused.

## Target-Owned Reconciliation

| Subject | Existing state | v0.16.0 requirement | Decision |
| --- | --- | --- | --- |
| Routine validation | bound to completed v0.15.1 workflow ID | bind the exact current execution profile | update only the workflow ID to `2026-09-06-ai-context-v0-16-0-upgrade`; preserve command, local `manual`, and CI `unconfigured` |
| Development orchestration | root guides route to `dev-workflow` | compatibility alias is retired | route current guidance to `software-development-orchestrator`; retain old identifier only in historical records |
| Target initialization | root guides route to `repo-structure-sync` | compatibility alias is retired | route current guidance to `ai-context-init`; retain old identifier only in historical records and the generated inventory's historical `generatedBy` value |
| Repository truth | target README and architecture language are target-owned | no source package may replace target facts | update only current skill names; retain product, stack and repository identity unchanged |

## Preserved Boundaries

- No product `src/**` or `tests/**` path is changed.
- No personal `.dev/ai-context/local/**` value is read or modified.
- Package-managed guides that v0.16.0 intentionally retains are not rewritten here.
- The existing commit grammar cutover and its one exact historical waiver remain unchanged.
- The final plan must be generated only after this reconciliation is committed and the worktree is clean.

## Transaction Checkpoint Corrections

Two fail-closed rollback checkpoints refined the final execution order without
changing the accepted 70-operation package delta:

1. Transaction `61c2245c57707cc77aaee15bdad8ee64ed920735854f40683a0e989215903e84`
   proved that the v0.16.0 target-gate projection must be committed before the
   sealed package transaction. The exact four-file projection was preserved,
   restored after rollback, and committed as `73e543683ebce3d0b697d34092d6eb2fd57ea2da`.
2. Transaction `d43203b4e19e16c16ae55c6dc05e3a2e18c9b40bdaab1c4ddbf2862927bf90ee`
   applied 70/70 operations and passed the target gate with 34/34 tests. Its
   finalization stopped before authority writes because the decision bound raw
   candidate JSON file digests, including the terminal LF, instead of the
   canonical JSON content digests required by the finalizer.

The corrected candidate authority identities are:

| Authority | Raw JSON file SHA-256 | Canonical JSON SHA-256 used by finalization |
| --- | --- | --- |
| Provenance | `46b7619b50783793af86202024545a49cbe557d91226dd4ccb991428d4f64743` | `2d4417f3333f909fe4c8ca48a36e844b6e6720320114a662c5aa31e6d6fa6866` |
| Customizations | `1b3c3ec0b4ae5e839fdc97fa555549c91bb1a22703edaba06c5f06a4e0f1ced9` | `cbf6b7ad0d7f9ee7f463580ab8fc8805b57729c389133c6417e0a3dde5a1c7eb` |

Both transactions are retained as Git-admin evidence and are terminally
rolled back. The next sealed plan must start from this documentation
checkpoint, bind the canonical candidate identities, and rerun only the short
target gate because its pending-receipt identity changes. Public package
download, incoming package validation, route analysis, and semantic
reconciliation remain reusable.
