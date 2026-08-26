# Upgrade Output Contract

Return these sections in order:

1. **Verdict**: `ready-to-plan`, `decision-required`, `ready-to-apply`, `validation-failed`, or `completed`.
2. **Version identity**: from/to release ID, tag, and full commit.
3. **Provenance and effective-state health**: valid fields, current catalog and
   target-authority digests, required packet freshness, missing evidence, and
   unresolved baseline.
4. **Change classification**: tables for automatic candidates and exclusions,
   plus a semantic reconciliation table keyed by customization ID and subject.
5. **Migration plan**: ordered actions, requested decisions, validation, and rollback boundary.
6. **Result**: applied paths, validation evidence, updated manifest and
   effective-rule/packet state, loaded-rule evidence, remaining overrides, and
   deferred items.

The semantic reconciliation table includes relationship, incoming equivalence,
proposed disposition, owner reconciliation, active-context audit,
post-upgrade audit, validation, and unresolved reason.

Do not report `completed` when fail-closed staged finalization did not complete,
required validation or post-upgrade audit failed, required state or packets are
missing/stale, or acknowledged reconciliation items remain unrecorded. Staged
publication rolls back on in-process failure; it does not claim cross-file
crash atomicity, and any stale or mixed crash residue must fail closed. A
read-only planning request stops before application and clearly states that no
files were changed.
