# Semantic Customization Lifecycle

Use this contract whenever a target changes a framework capability, rule,
constraint, or contract. Paths are supporting evidence; they are never the
primary identity.
The machine-readable ledger schema is
`../templates/customizations.schema.yaml`.
The target-effective state and packet contracts are
`../templates/effective-rule-state.schema.yaml` and
`../templates/effective-rule-packet.schema.yaml`.

These authorities apply only to `initialized-target` mode. Framework-source
action execution is governed separately by
`.dev/standards/AI-CONTEXT-SOURCE-EFFECTIVE-RULES.yaml`; its evidence is
transient, source-only, and cannot create or satisfy target provenance,
customization, effective-state, or packet truth.

## Authorities

- `.dev/ai-context/provenance.yaml` records the installed framework source,
  selected components, ledger identity, and finalized migration.
- `.dev/ai-context/customizations.yaml` records target semantic intent and its
  reconciliation lifecycle.
- `.dev/ai-context/effective-rules.yaml` records the complete, target-owned
  resolved state for adopted rule and constraint identities. It pins framework
  and catalog evidence, provenance and customization digests, explicit
  dispositions, and deterministic request routing; it is not a copy of the
  framework baseline.
- `.dev/ai-context/effective-rule-packets/**` holds derived, task-scoped packet
  projections. A packet retains each full effective normative statement, its
  baseline catalog binding, and the complete matching target disposition
  record; it may be consumed only while its state and catalog inputs remain
  fresh.
- Requirement, ADR, and workflow records justify decisions.
- Target enterprise test and permission policies remain target-owned truth
  unless they change framework behavior, in which case record the semantic
  difference.
- `.dev/AI-CONTEXT-SOURCE.yaml` is legacy read compatibility only. Never keep it
  active beside component-aware provenance.

## Lifecycle

1. **Initialize**: with credible release repository, release ID, version, tag,
   full commit, selection, and import-timestamp evidence,
   `ai-context-init` publishes provenance and the empty ledger through
   fail-closed staged publication with rollback on in-process failure. When
   verified catalog `catalog_digest.value` records plus explicit target
   acceptance/applicability and deterministic routing evidence are also
   supplied, it publishes packets first and the completed effective-rule state
   last. An in-process exception rolls the staged publication back. A process
   crash is not cross-file atomic, but stale, mixed, old, or new state cannot
   pass the digest/freshness gates and therefore fails closed. Otherwise
   initialization reports a derived action readiness result of
   `action_ready: false`, `status: unresolved`, and reason
   `effective-rule-state-missing`; no empty effective-rule state or packet is
   created, and routine action work remains fail-closed until owner
   reconciliation generates them. This readiness result is not a provenance
   authority field. Incomplete credible-source evidence returns unresolved
   provenance and writes none of those files.
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
   owner decision, validation, and unresolved reason. It also compares pinned
   catalog and target-authority digests before accepting any effective state.
5. **Reconcile**: governance applies only the approved retain, merge,
   supersede, or retire decision. Paths alone never prove equivalence. It
   records the proposed complete final effective normative statement for an
   active retain/merge semantic delta and prepares the state/packet regeneration
   inputs; no action skill performs its own directory scan and no candidate is
   published before independent verification.
6. **Verify**: the auditor performs a separate post-upgrade assessment of the
   active context. A baseline assessment cannot serve as verification.
7. **Finalize**: after the approved reconciliation and both audit records satisfy
   the finalization gate, publish the finalized target authorities, regenerate
   affected packets, and publish the completed target-effective state last.
   Validate the resulting provenance, ledger, state, and packets. In-process
   failure restores the prior authority/state bytes and leaves the candidate
   migration unresolved; crash-mixed state remains fail-closed.

## Fail-Closed Rules

- Reject absolute paths, backslashes, empty segments, `.`/`..`, duplicate IDs,
  self-dependencies, missing dependency IDs, and path-first identities.
- Require base framework version, full commit, and evidence; require at least
  one requirement, ADR, or workflow decision reference.
- Require owner, decision status, decision time, and evidence for approved
  reconciliation.
- Require active-context baseline audit evidence before equivalence analysis.
- Require explicit, verified target evidence before recording a
  `baseline-effective` disposition. Never infer it from a framework default or
  an omitted target record.
- Require an exact deterministic route for a capability, execution mode,
  technology profile, and file type. The route's packet must match the current
  target-state and catalog digests, report the exact not-applicable subset, and
  retain each selected rule's full effective normative statement, baseline
  catalog binding, and complete disposition projection.
- Reject a target semantic delta that supplies only a patch, partial text, or
  temporary summary, or whose CUST identity does not name the same rule with an
  approved, finalized, active retain/merge reconciliation.
- Missing, stale, unknown, ambiguous, unpacketized, or invariant-conflicting
  effective state is unresolved. Stop rather than silently loading framework
  defaults or a nearby profile document.
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
  application, effective-state and packet regeneration, and provenance
  finalization.
