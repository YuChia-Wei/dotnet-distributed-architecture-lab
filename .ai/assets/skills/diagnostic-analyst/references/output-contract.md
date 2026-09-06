# Diagnostic Output Contract

Retain a JSON record when machine validation is needed. All fields below are
required; unknown fields fail closed. Nonempty text describes actual evidence,
not placeholders. Empty evidence lists are allowed only for unexecuted or
unconfirmed work. The validator does not execute commands in the record.

```text
schema_version: "1.0"
diagnostic_id: nonempty identifier
symptom: {description, expected, actual, scope}
hypotheses: [{
  id, claim, falsifying_observation,
  method: interception | counting | enumeration | controlled-experiment | sampling | static-inspection | not-run,
  falsification_strength: deterministic-complete | deterministic-bounded | sampling-limited | not-executed,
  observation_scope,
  coverage: {expected_opportunities: integer >= 0, observed_opportunities: integer >= 0, complete: boolean},
  result: supported | falsified | inconclusive | not-tested,
  observation, evidence_refs: [evidence id]
}]
minimal_reproduction: {
  status: reproduced | not-reproduced | not-run | blocked,
  command, environment, expected, actual, evidence_refs: [evidence id]
}
causal_isolation: {
  status: isolated | not-isolated | not-run | blocked,
  baseline, intervention, actual, alternatives, evidence_refs: [evidence id]
}
root_cause: {
  status: confirmed | unconfirmed | blocked,
  hypothesis_ids: [hypothesis id], explanation, limitations, evidence_refs: [evidence id]
}
repair_handoff: {owner_skill, scope, authorization_ref: nonempty string | null}
regression_binding: {status: proposed | verified, command, evidence_refs: [evidence id]}
evidence: [{id, path: relative POSIX path, sha256: lowercase SHA-256}]
```

Run:

```sh
python .ai/assets/skills/diagnostic-analyst/scripts/validate-diagnostic-record.py --record diagnostic.json --evidence-root evidence
```

Evidence paths resolve only inside the explicit evidence root. Symlink/reparse
components, absolute paths, traversal, missing files, and hash disagreement
fail. The root and record are read-only. Store privacy-safe command output,
subject and environment identity, and bounded observations there; exclude
secrets and unnecessary personal paths. References bind bytes, not execution
truth. A schema-valid synthetic fixture is never actual incident evidence.

Project a human report in this order: symptom; hypothesis table (including
falsifier, method, strength, coverage and observation); minimal reproduction;
causal isolation; root cause and limits; repair handoff; regression binding.
Preserve `unconfirmed` and `blocked` states verbatim. Historical worked examples
are instructional interpretations, not a rerun or newly confirmed diagnosis.
