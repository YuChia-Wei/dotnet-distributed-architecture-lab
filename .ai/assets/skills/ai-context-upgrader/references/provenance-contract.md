# Target Provenance Contract

The v0.6.0 installed target manifest path is
`.dev/ai-context/provenance.yaml`. Create it with the adjacent target-owned
`.dev/ai-context/customizations.yaml` ledger during initialization or governed
upgrade reconciliation. When explicit effective-state evidence is available,
create the adjacent `.dev/ai-context/effective-rules.yaml` state and packets
under `.dev/ai-context/effective-rule-packets/` through fail-closed staged
publication: packets first, state last, with rollback on in-process failure. A
process crash is not cross-file atomic, but no stale or mixed candidate may
pass the digest/freshness gates. If that evidence is not available, retain
structural initialization with
derived action readiness `action_ready: false`, `status: unresolved`, and
reason `effective-rule-state-missing`; create no empty state or packet, and
keep routine action work fail-closed until owner reconciliation. The readiness
result is derived output, not a provenance authority field.

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
- `effective_rules.state` is `.dev/ai-context/effective-rules.yaml`,
  `effective_rules.packets_root` is `.dev/ai-context/effective-rule-packets/`,
  and both use the supported effective-rule schema version.
- The target-effective state pins the current provenance and customization
  digests, framework version and commit, selected profile, and fixed shared and
  selected-profile catalog paths and verified `catalog_digest.value` values.
  Its deterministic digest and each route packet digest must verify before an
  action uses them.
- Customization and unresolved-item IDs are unique and stable within the target repository.
- `last_migration.to_version` equals `source.version` after a completed upgrade.

## Mutation Rules

- With credible source and selection evidence, `ai-context-init` uses
  fail-closed staged publication with in-process rollback for initial
  provenance and an empty customization ledger. With verified catalogs plus
  explicit target adoption/applicability and routing evidence, it additionally
  stages the required packets first and publishes the completed effective-rule
  state last. A process crash is not cross-file atomic; any stale or mixed
  candidate remains invalid. Without that latter evidence, it returns
  derived action readiness as `action_ready: false`, `status: unresolved`, and
  reason `effective-rule-state-missing`, creates no empty effective-rule state
  or packet, and awaits owner reconciliation. The deprecated
  `repo-structure-sync` compatibility entry follows the same contract during
  its transition. Incomplete credible-source evidence produces an unresolved
  no-write result.
- `ai-context-upgrader` reads it during planning and uses fail-closed staged
  finalization with rollback on in-process failure only after owner
  reconciliation, independent post-upgrade audit, and target validation. It
  does not claim cross-file crash atomicity.
- Do not delete customizations merely because incoming framework paths changed;
  reconcile capability, rule, or contract equivalence and disposition.
- Do not change the source version to describe a partially applied or failed upgrade. Record such work under `reconciliation.unresolved` while retaining the last validated source.
- Do not treat an omitted rule record, a cached packet, or an action skill's
  memory as baseline acceptance. Missing, stale, ambiguous, unknown,
  unpacketized, or invariant-conflicting state fails closed until owner
  reconciliation regenerates the target-effective state and packets.
- The framework source repository stores the template only; it must not carry a self-referential target instance.

The governance-owned
`../../ai-context-governance/references/semantic-customization-lifecycle.md`
defines the ledger fields and four-skill lifecycle. The machine-readable schema
set is `../../ai-context-governance/templates/customizations.schema.yaml`,
`../../ai-context-governance/templates/effective-rule-state.schema.yaml`, and
`../../ai-context-governance/templates/effective-rule-packet.schema.yaml`.

Ordinary target-only requirements, ADRs, workflows, runbooks, maintenance
windows, test commands, enterprise network rules, and permission policies are
protected target truth. Record them in the ledger only when they change
framework-managed behavior. If an incoming release later introduces the same
path or contract, add unresolved reconciliation rather than inferring overwrite
authority.
