# Engineering Identity Contract

Contract ID: `ENG-IDENTITY-001`.

This is the canonical portable universal baseline contract for engineering
identity. The source-governance registry in
[AI Context Rule Ownership](../../../../.dev/standards/AI-CONTEXT-OWNERSHIP.md)
classifies each artifact's single canonical owner; it does not duplicate this
contract's semantic content.

## Load The Relevant Identity, Not A Whole Directory

An action consumes the freshness-validated, task-scoped effective rule packet
selected by the shared resolver. It does not scan every `.dev/` or `.ai/`
document and it does not replace missing target-effective state with remembered
framework defaults.

The packet identifies the applicable `concept_id`, `rule_id`, and
`constraint_id`, retains their full normative statements, and records the
baseline version and target-state digest. Load abstract enforcement capability
or technology-binding details only when implementation, validation, upgrade,
or diagnostic handling needs them.

For registered universal rules, the portable baseline is
`engineering-rule-catalog.yaml` in this directory. It preserves the full
anchored source statement and source-governance provenance. For profile rules,
the resolver uses the profile catalog as an exact projection of the profile
Markdown owner. Neither catalog allocates a missing path-derived identity;
unregistered documents remain unpacketized and fail closed.

## Identity Boundary

- Concepts, rules, and constraints express engineering meaning.
- Abstract capabilities express enforcement classes, such as static analysis,
  executable tests, or human review.
- Technology bindings connect a selected profile's capability to a constraint.
- Providers, analyzers, runtime validators, Diagnostics, package versions,
  commands, and target configuration are implementation details of a binding;
  they are never substitutes for semantic identities.

References are explicit `(kind, id)` pairs. Missing, duplicate, ambiguous, or
type-invalid references are unresolved and fail closed. File moves, provider
changes, diagnostic renumbering, and package upgrades retain the identity when
meaning is unchanged; a changed meaning requires explicit owner-approved
supersession.

## Portable Baseline Boundary

Cross-technology baseline semantics belong under `.ai/assets/shared/`.
Profile-only baseline defaults, rules, constraints, technology bindings, and
bundled tooling belong under `.ai/assets/tech-stacks/<profile>/`. The source
registry and governance remain under `.dev/standards/`; target-effective truth
belongs under `.dev/ai-context/` and is shared by humans and agents. A
current record with a legacy `.dev/standards/` `canonical_path` is
`transitional-unmigrated` until the migration matrix reclassifies it, but no
other consumer may create a second owner while it is migrated.
