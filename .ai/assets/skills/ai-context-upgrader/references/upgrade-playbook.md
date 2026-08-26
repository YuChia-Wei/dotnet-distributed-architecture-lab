# Upgrade Playbook

## Entry Gate

Read, in order:

1. target `AGENTS.md` and any deeper instructions;
2. `.dev/standards/AI-CONTEXT-VERSION-POLICY.md` from the requested framework version;
3. target `.dev/ai-context/provenance.yaml`, referenced
   `.dev/ai-context/customizations.yaml`, and
   `.dev/ai-context/effective-rules.yaml` with its required packets, or the
   legacy `.dev/AI-CONTEXT-SOURCE.yaml`;
4. requested package metadata and migration guide, including the immutable
   source identity carried by the trusted package;
5. the three-way boundary and output contract in this skill.

When a release migration guide projects a workflow file-disposition manifest,
treat `kept`, `moved-to`, `merged-into`, and `retired` as incoming intent only.
The projected disposition can improve path discovery, but it cannot establish
the target's base bytes, ownership, local changes, or write authorization.

Use `ai-context-init` if no initialization has occurred; the deprecated
`repo-structure-sync` entry follows that contract during transition. If
framework files exist but provenance is absent, stop automatic upgrade
classification and produce an unresolved-provenance inventory. The user must
identify a credible base or authorize a manual baseline reconciliation.

When provenance and the customization ledger exist but the derived readiness
result is `action_ready: false`, `status: unresolved`, with reason
`effective-rule-state-missing`, retain that structural initialization, create
no synthetic empty effective-rule state, and return a decision-required
fail-closed result. Owner reconciliation must supply the missing target
adoption/applicability or routing evidence before effective state and packets
are generated or routine action work proceeds.

When only the legacy manifest exists, convert every `local_overrides` entry
one-to-one into `reconciliation.unresolved` with reason
`legacy-local-override`. Preserve its evidence and do not invent capability,
rule, or contract identity. If legacy and schema-2 provenance both exist, fail
closed until the duplicate authority is reconciled.

## Discovery

- Validate target provenance with
  `.ai/scripts/validate-ai-context-target.py`; downstream validation does not
  require source release registries, publication workflows, or local Git tags.
- Bind the requested version to the package's immutable repository, release ID,
  tag, and full commit evidence.
- Verify the effective state's pinned shared and selected-profile catalog paths
  and digests, provenance/customization digests, deterministic target-state
  digest, and every packet needed by the requested route. Missing, stale,
  unknown, ambiguous, unpacketized, or invariant-conflicting state is an
  unresolved stop, not permission to use incoming framework defaults.
- Preserve a clean rollback point for target-local work before applying changes.
- Use package inventories and the recorded base identity for three-way
  discovery. Use source Git comparison only when the source repository is
  deliberately available; never make it a downstream prerequisite.
- Read migration guides for every skipped version between the recorded and requested releases.

## Planning

Classify each relevant framework change as `automatic-candidate`, `reconcile`, or `exclude`. An automatic candidate is not authorization to write. Group reconciliation items by target owner and explain what would be lost under replacement.

The plan must state:

- from/to release ID, version, tag, and commit;
- manifest state and unresolved provenance;
- changed paths by classification and reason;
- incoming file dispositions and their target-side three-way classification;
- ordered migrations and validation;
- rollback boundary;
- items requiring user decision.
- a semantic reconciliation table keyed by customization ID, with subject,
  relationship, incoming equivalence, proposed disposition, owner decision,
  validation, and unresolved reason.
- every selected framework-managed package path that target Git ignore or
  exclude rules suppress, including the exact path, component, ownership, and
  matched rule. Keep it unresolved until the owner chooses to preserve the
  rule, add a narrow exception, disable the component, or retain a pending
  decision; never modify target-owned ignore configuration automatically.
- every effective-rule disposition that needs explicit baseline acceptance,
  target semantic-delta reconciliation, enforcement tuning, tooling-waiver
  reconsideration, or not-applicable predicate verification; and
- the deterministic route records and packets that must be regenerated after
  accepted reconciliation.

## Application

### Routine Validation Policy

Treat `.dev/project-config.yaml#validation.routine` as target-owned policy. Add
missing defaults only through reconciliation; do not overwrite local or CI
selections. Defaults are local `manual` and CI `unconfigured`. Preserve ignored
`.dev/validation.local.conf` without reading or changing it. Lifecycle
validation remains unaffected.

Apply only explicitly accepted paths. Never use a bulk copy over the repository root. Re-read a path immediately before writing when it is target-owned or previously classified for reconciliation.

When package preflight reports an ignored selected framework-managed path, do
not acknowledge it as an ordinary reconciliation item or write any package
bytes. Resolve the target-owned rule only through the owner's recorded
disposition, then create a new plan. The pending apply receipt carries the
required framework path/component/ownership/byte identity so the target
validator, critical gate, and provenance finalization reject the same missing,
changed, or still-ignored payload.

For `moved-to` or `merged-into`, preserve target-local source content until its
destination has been reconciled. For `retired`, remove automatically only when
the target source is byte-identical to base and the migration guide explicitly
permits automatic removal. A disposition marked `kept` remains a normal
three-way candidate; it is not a force-replace instruction.

After changes, request an independent post-upgrade `ai-context-auditor`
assessment, run `.ai/scripts/validate-ai-context-target.py`, and then run the
target's required repository gate. If any check fails, retain the previous
provenance bytes and report rollback options.

Regenerate effective-rule state and only the packets selected by verified route
records after reconciliation. Each target semantic delta must carry its complete
final effective normative statement and digest from an approved, finalized,
active retain/merge reconciliation. Each packet must carry the full effective
statements, their catalog baseline bindings, exact complete target disposition
projections, loaded IDs, baseline version/commit, target-state digest, catalog
digests, exact request dimensions, resolver version, and execution evidence.
An action skill must consume this freshness-validated packet; it must not
re-scan target documentation or silently fall back to framework defaults.

## Completion

Finalize `.dev/ai-context/customizations.yaml` and
`.dev/ai-context/effective-rules.yaml`, its required packets, and
`.dev/ai-context/provenance.yaml` only after owner reconciliation, independent
post-upgrade verification, and target validation succeed. Keep legacy path
overrides and collisions in `reconciliation.unresolved`. Report the exact
resulting version and commit, validation evidence, remaining customizations,
and deferred migration. Required framework-managed package paths must have
landed with their expected bytes and remain visible to target Git before
finalization; otherwise preserve prior provenance bytes. Do not retain the
legacy manifest as a second authority after a successful schema-2 migration.
