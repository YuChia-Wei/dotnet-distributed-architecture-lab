# Output Contract

When credible import evidence identifies the framework repository, release ID,
version, tag, full commit, component selection, and import time, publish
`.dev/ai-context/provenance.yaml` and
`.dev/ai-context/customizations.yaml` from the canonical templates after
target validation succeeds using fail-closed staging with rollback on
in-process failure. When explicit target adoption/applicability evidence,
current verified catalog `catalog_digest.value` records, and deterministic
route selections are supplied, publish required packets first and the completed
`.dev/ai-context/effective-rules.yaml` last. A process crash is not cross-file
atomic; stale or mixed candidates fail digest/freshness verification. Otherwise
report derived action readiness as `action_ready: false`, `status: unresolved`,
and reason `effective-rule-state-missing`; create no empty effective state or
packet, and report the owner reconciliation required before routine action
work. This readiness result is not a provenance field. If the copied source
cannot be proven, report unresolved provenance and write none of those
provenance, ledger, state, or packet files. Never retain
`.dev/AI-CONTEXT-SOURCE.yaml` beside schema-2 provenance.

## Phase 1 Output

The low-cost inventory pass should return these sections in order:

1. `Evidence Used`
2. `Target Repository Mode`
3. `Confirmed Repo Facts`
4. `Project Config Decision`
5. `Copied or Stale Template Facts`
6. `P0 Hits`
7. `P1 Hits`
8. `Complexity Verdict`
9. `Safe Direct Updates`
10. `Escalation Targets`
11. `Source Packet`

## Phase 2 or Final Output

After edits are made, return:

1. `Docs Updated`
2. `Project Config Generated or Deferred`
3. `Inferred or Missing Truth`
4. `Template Facts Removed or Preserved`
5. `Recommended Next Step`

When translation is requested, append `Translation Parity` using the `context-translator` return. If a low-cost runtime/model is unavailable, record translation as deferred instead of performing it in the main pass.
