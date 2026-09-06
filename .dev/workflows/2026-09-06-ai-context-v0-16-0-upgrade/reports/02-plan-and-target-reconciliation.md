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
