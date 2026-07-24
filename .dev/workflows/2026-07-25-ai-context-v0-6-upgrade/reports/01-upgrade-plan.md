# AI Context v0.6.0 Upgrade Plan

## Status

- Verdict: `ready-to-apply-v0.5.0`
- Target provenance: valid `REL-v0.4.0`
- Requested release: published `REL-v0.6.0`
- Required route: `v0.4.0 -> v0.5.0 -> v0.6.0`
- Applied changes: none

## Discovery Summary

The source registry and annotated tags agree on all required identities.
`REL-v0.5.0` declares v0.4.0 as an exact automatic source. `REL-v0.6.0`
declares only v0.5.0, so the intermediate validation and provenance checkpoint
cannot be skipped.

Initial Git-backed three-way discovery for v0.4.0-to-v0.5.0 classified:

- 81 automatic candidates;
- 63 reconciliation paths;
- 171 source-only exclusions.

The package planner is authoritative for the exact installable payload and
operation IDs. The immutable package validation and exact dry plan are recorded
in `02-v0.5.0-package-plan.md`.

## Reconciliation Defaults

- Preserve every path already declared in `.dev/AI-CONTEXT-SOURCE.yaml`.
- Preserve root repository identity and collaboration files.
- Preserve target workflow, assessment, backlog, requirement, spec, ADR,
  architecture, operations, domain-language, and project-configuration truth.
- Adopt incoming canonical framework semantics only after path-level review.
- Exclude source repository instances and publication history.

## Validation And Rollback

- Rollback commit: `2eeddf392ca79deb4407c47d13ad53178015ba90`.
- Validate archive sidecars, inventories, member checksums, and ZIP/tar parity.
- Run the target's AI-context and workflow gates plus the full required gate
  after each stage.
- Do not advance provenance after a failed stage.
