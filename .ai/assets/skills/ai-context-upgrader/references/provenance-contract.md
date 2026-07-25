# Target Provenance Contract

The v0.6.0 installed target manifest path is
`.dev/ai-context/provenance.yaml`. Create it with the adjacent target-owned
`.dev/ai-context/customizations.yaml` ledger during initialization or governed
upgrade reconciliation.

`.dev/AI-CONTEXT-SOURCE.yaml` remains a schema-1 read-compatibility input for
older targets. Migrate it to the grouped path before writing schema 2. Never
retain both files as active authorities.

## Required Invariants

- `schema_version` is supported by the active upgrader.
- `source.repository` is a stable repository identity, not a local temporary path.
- `source.release_id` equals `REL-` plus `source.version`.
- `source.version` and `source.tag` are equal SemVer tags.
- `source.commit` is a full lowercase 40-character Git SHA and resolves to the tag when the source Git repository is available.
- `installation.imported_at` and non-null upgrade timestamps use ISO 8601 with an offset.
- Selected mandatory components, profiles, and providers are explicit.
- `customizations.ledger` is `.dev/ai-context/customizations.yaml`.
- Customization and unresolved-item IDs are unique and stable within the target repository.
- `last_migration.to_version` equals `source.version` after a completed upgrade.

## Mutation Rules

- `ai-context-init` atomically creates initial provenance and an empty
  customization ledger only from credible source and selection evidence. The
  deprecated `repo-structure-sync` compatibility entry follows the same
  contract during its transition. Incomplete evidence produces an unresolved
  no-write result.
- `ai-context-upgrader` reads it during planning and atomically finalizes it
  only after owner reconciliation, independent post-upgrade audit, and target
  validation.
- Do not delete customizations merely because incoming framework paths changed;
  reconcile capability, rule, or contract equivalence and disposition.
- Do not change the source version to describe a partially applied or failed upgrade. Record such work under `reconciliation.unresolved` while retaining the last validated source.
- The framework source repository stores the template only; it must not carry a self-referential target instance.

The governance-owned
`../../ai-context-governance/references/semantic-customization-lifecycle.md`
defines the ledger fields and four-skill lifecycle. The machine-readable schema
is `../../ai-context-governance/templates/customizations.schema.yaml`.

Ordinary target-only requirements, ADRs, workflows, runbooks, maintenance
windows, test commands, enterprise network rules, and permission policies are
protected target truth. Record them in the ledger only when they change
framework-managed behavior. If an incoming release later introduces the same
path or contract, add unresolved reconciliation rather than inferring overwrite
authority.
