# AI Context Version Policy

## Purpose And Portable Boundary

This portable policy defines published framework version identity, target
provenance, compatibility interpretation, and target upgrade safety. It is the
content mapped to `.dev/standards/AI-CONTEXT-VERSION-POLICY.md` in an installed
target.

Source framework version-candidate preparation, source release validation,
repository tag handoff, hosted publication, provider reconciliation, and
hosted finalization are upstream source-repository responsibilities. They are
not target instructions and are intentionally absent from this policy.

## Published Framework Version Identity

- A published framework version uses a SemVer tag in the form
  `vMAJOR.MINOR.PATCH` and a stable release identifier in the form
  `REL-vMAJOR.MINOR.PATCH`.
- Trusted package metadata binds the source repository, release ID, annotated
  tag, and full lowercase 40-character commit. A mutable branch, workflow ID,
  date, local checkout path, or package filename is not a substitute.
- A published annotated tag is immutable. A target must never move, recreate,
  delete, or reuse it.
- Target adoption requires trusted published package/version evidence. A local
  file copy, repository integration event, workflow completion, or bare
  `validated` claim does not establish a published framework version.

## SemVer Compatibility Meaning

| Change | Version impact |
| --- | --- |
| Removes or incompatibly changes a stable collaboration entry, manifest schema, skill input/output contract, or required target integration | major |
| Adds a backward-compatible skill, rule, validation, runtime route, or target migration capability | minor |
| Corrects wording, links, metadata, or implementation defects without intentionally changing a public contract | patch |

While the framework remains below `v1.0.0`, a minor version may declare
breaking changes. Trusted release metadata must identify the affected
contracts and provide explicit migration guidance. A patch must not
intentionally break a published contract.

## Target Provenance

An initialized target records its installed framework source in
`.dev/ai-context/provenance.yaml` and its target-owned semantic decisions in
`.dev/ai-context/customizations.yaml`. Provenance records:

- source repository, published version, release ID, annotated tag, and full
  commit;
- import and last-upgrade timestamps;
- manifest schema version and selected components/profiles/providers;
- the customization ledger path;
- the last completed migration and unresolved reconciliation items; and
- effective-rule state and packet bindings when verified target evidence makes
  them available.

`.dev/AI-CONTEXT-SOURCE.yaml` is schema-1 read compatibility for older targets.
Migrate it to the grouped path before writing schema 2 and never retain both as
active authorities. The framework source repository stores templates, not a
self-referential target manifest.

## Target Upgrade Classification

An upgrade compares three states:

1. the previous published framework version recorded by the target;
2. the requested published framework version and trusted package inventory;
3. the target repository's current files and declared customizations.

Classify each relevant incoming path before writing:

- `automatic-candidate`: incoming reusable content is byte-identical to the
  recorded base in the target and may be proposed for replacement;
- `reconcile`: target-owned, locally changed, missing-provenance, ignored, or
  semantically ambiguous content requires an owner decision;
- `exclude`: source-repository history/runtime material that does not belong in
  the target.

`automatic-candidate` is a migration category, not write authorization, a
package candidate, or a framework release state. Apply only owner-accepted
paths after three-way and semantic reconciliation.

Source workflow/assessment/release instances, source backlog, Git metadata,
tool caches, and product `src/` or `tests/` trees are excluded by default.
Reusable governance, templates, and selected framework assets remain normal
package candidates subject to ownership and three-way rules.

## Target Upgrade Completion

Finalize `.dev/ai-context/provenance.yaml`, customizations, and any selected
effective-rule state only after owner reconciliation, independent post-upgrade
audit, package/target validation, and target-required repository gates pass.
Missing source identity, unresolved refs, stale digests, ignored required
managed paths, or unacknowledged reconciliation items fail closed and preserve
the last validated target provenance.

Target upgrade completion describes installed target state. It does not imply
source repository integration, source release validation, hosted publication,
or publication finalization.

## Target Validation

Use the installed target validator and target-owned routine/CI selections.
Downstream target validation does not require source release registries,
source publication workflows, local source tags, or source-maintainer
credentials.

Target upgrade application and target provenance finalization require their own
explicit authorization. No version label, migration category, or validation
result grants unrelated write or publication authority.
