# Durable Backlog

This target-owned directory stores durable cross-workflow work items when the
target selects the provider-neutral `repo-backlog` capability. It is not a
workflow engine and it is never activated merely because the directory exists.

## Ownership Boundary

- `INDEX.MD` catalogs the target's selected durable work items.
- `items/<item-id>.yaml` may own one target work item when the target enables
  the repository-backlog provider.
- `.dev/assessments/` owns observations and finding evidence.
- `.dev/workflows/` owns authorized execution plans, tasks, validation
  evidence, and resumable checkpoints.
- The target's validated provenance selects whether repository backlog binding
  is `required`, `optional`, or `disabled` and whether existing target records
  are preserved.

A backlog item, external provider state, workflow, or repository file never
authorizes work by itself. Record explicit owner authorization through the
target's selected work-item binding contract. Do not copy source-repository
GitHub identities, Project fields, release allocations, or historical backlog
records into a target during initialization.

## Provider Neutrality

Targets may use GitHub, Azure DevOps, another tracker, a repository backlog, or
no tracker according to target-owned policy. Provider identities and mutable
read-back state belong to target-owned provider receipts, not to this portable
capability contract.
