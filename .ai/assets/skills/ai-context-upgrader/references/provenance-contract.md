# Target Provenance Contract

The installed target manifest path is `.dev/AI-CONTEXT-SOURCE.yaml`. Create it from the skill template during initial synchronization, or during a manual baseline reconciliation for an older unversioned installation.

## Required Invariants

- `schema_version` is supported by the active upgrader.
- `source.repository` is a stable repository identity, not a local temporary path.
- `source.release_id` equals `REL-` plus `source.version`.
- `source.version` and `source.tag` are equal SemVer tags.
- `source.commit` is a full lowercase 40-character Git SHA and resolves to the tag when the source Git repository is available.
- `installation.imported_at` and non-null upgrade timestamps use ISO 8601 with an offset.
- Override and unresolved-item IDs are unique and stable within the target repository.
- Every override has at least one repository-relative path, a reason, an owner, and an upgrade disposition.
- `last_migration.to_version` equals `source.version` after a completed upgrade.

## Mutation Rules

- `repo-structure-sync` creates initial provenance after target initialization validates.
- `ai-context-upgrader` reads it during planning and updates it after upgrade validation.
- Do not delete overrides merely because the incoming framework no longer contains their paths; reconcile their disposition.
- Do not change the source version to describe a partially applied or failed upgrade. Record such work under `reconciliation.unresolved` while retaining the last validated source.
- The framework source repository stores the template only; it must not carry a self-referential target instance.

`local_overrides` records a target deviation from a framework-managed path or contract. Ordinary target-only domain artifacts that never existed in the base or incoming framework, such as a project requirement, are protected target truth but are not framework overrides. If an incoming release later introduces the same path or contract, add an unresolved reconciliation item; record an override only if the target chooses to retain a deviation from the incoming framework-managed content.
