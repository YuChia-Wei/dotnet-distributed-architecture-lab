# Semantic Customization Lifecycle

Use this contract whenever a target changes a framework capability, rule, or
contract. Paths are supporting evidence; they are never the primary identity.
The machine-readable ledger schema is
`../templates/customizations.schema.yaml`.

## Authorities

- `.dev/ai-context/provenance.yaml` records the installed framework source,
  selected components, ledger identity, and finalized migration.
- `.dev/ai-context/customizations.yaml` records target semantic intent and its
  reconciliation lifecycle.
- Requirement, ADR, and workflow records justify decisions.
- Target enterprise test and permission policies remain target-owned truth
  unless they change framework behavior, in which case record the semantic
  difference.
- `.dev/AI-CONTEXT-SOURCE.yaml` is legacy read compatibility only. Never keep it
  active beside component-aware provenance.

## Lifecycle

1. **Initialize**: `ai-context-init` creates provenance and the empty ledger
   as one atomic change only from a credible release repository, release ID,
   version, tag, full commit, selection, and import timestamp. With incomplete
   evidence, return unresolved provenance and write neither authority.
2. **Record**: `ai-context-governance` assigns a stable customization ID,
   identifies a capability/rule/contract before paths, records why the target
   behavior differs or extends the framework, records base framework evidence
   and dependencies, links decision evidence, and obtains an owner
   reconciliation decision.
3. **Baseline**: `ai-context-auditor` verifies that the active context implements
   the recorded semantics and records an independent assessment reference.
4. **Compare**: `ai-context-upgrader` compares each subject with the incoming
   framework and emits a semantic reconciliation table: customization ID,
   subject, current relationship, incoming equivalence, proposed disposition,
   owner decision, validation, and unresolved reason.
5. **Reconcile**: governance applies only the approved retain, merge,
   supersede, or retire decision. Paths alone never prove equivalence.
6. **Verify**: the auditor performs a separate post-upgrade assessment of the
   active context. A baseline assessment cannot serve as verification.
7. **Finalize**: validate provenance and ledger, then update provenance. Any
   failure preserves the prior provenance bytes and leaves the candidate
   migration unresolved.

## Fail-Closed Rules

- Reject absolute paths, backslashes, empty segments, `.`/`..`, duplicate IDs,
  self-dependencies, missing dependency IDs, and path-first identities.
- Require base framework version, full commit, and evidence; require at least
  one requirement, ADR, or workflow decision reference.
- Require owner, decision status, decision time, and evidence for approved
  reconciliation.
- Require active-context baseline audit evidence before equivalence analysis.
- `retire` and `supersede` require explicit owner approval and verified
  post-upgrade audit evidence.
- Finalized non-unresolved entries require approved owner reconciliation and
  verified post-upgrade audit evidence.
- Convert each legacy schema-1 `local_overrides` entry only to one
  `reconciliation.unresolved` item with reason `legacy-local-override`.
  Preserve its ID, paths, owner, reason, and disposition as evidence; never
  invent a semantic subject or ledger entry.

## Skill Boundaries

- `ai-context-init`: initialization and credible source evidence.
- `ai-context-governance`: ledger ownership and owner reconciliation.
- `ai-context-auditor`: read-only baseline and post-upgrade verification.
- `ai-context-upgrader`: three-way comparison, reconciliation table, validated
  application, and provenance finalization.
