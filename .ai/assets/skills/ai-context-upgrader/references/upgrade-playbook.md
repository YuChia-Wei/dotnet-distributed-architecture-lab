# Upgrade Playbook

## Entry Gate

Read, in order:

1. target `AGENTS.md` and any deeper instructions;
2. `.dev/standards/AI-CONTEXT-VERSION-POLICY.md` from the requested framework version;
3. target `.dev/ai-context/provenance.yaml` and referenced
   `.dev/ai-context/customizations.yaml`, or the legacy
   `.dev/AI-CONTEXT-SOURCE.yaml`;
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

## Application

Apply only explicitly accepted paths. Never use a bulk copy over the repository root. Re-read a path immediately before writing when it is target-owned or previously classified for reconciliation.

For `moved-to` or `merged-into`, preserve target-local source content until its
destination has been reconciled. For `retired`, remove automatically only when
the target source is byte-identical to base and the migration guide explicitly
permits automatic removal. A disposition marked `kept` remains a normal
three-way candidate; it is not a force-replace instruction.

After changes, request an independent post-upgrade `ai-context-auditor`
assessment, run `.ai/scripts/validate-ai-context-target.py`, and then run the
target's required repository gate. If any check fails, retain the previous
provenance bytes and report rollback options.

## Completion

Finalize `.dev/ai-context/customizations.yaml` and
`.dev/ai-context/provenance.yaml` only after owner reconciliation, independent
post-upgrade verification, and target validation succeed. Keep legacy path
overrides and collisions in `reconciliation.unresolved`. Report the exact
resulting version and commit, validation evidence, remaining customizations,
and deferred migration. Do not retain the legacy manifest as a second
authority after a successful schema-2 migration.
