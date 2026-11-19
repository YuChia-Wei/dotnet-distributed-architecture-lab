# Synthetic promotion example

This is a shape example, not an execution transcript, actual proposal or adoption.
No listed file was created. Replace every angle-bracket placeholder with ACTUAL
values and choose explicit platform-appropriate absolute paths. Do not send a
placeholder request and call its failure a verification of the intended lifecycle.

## Project-owned bindings

The project already has one UTF-8 rule file and selected source evidence. Its owner
may author a config like this; separate evidence roots retain the project process:

```json
{
  "config_version": 2,
  "skills": {
    "standards-promotion": {
      "store": {
        "root": "knowledge/proposals"
      }
    }
  },
  "constraints": {
    "standards-promotion": {
      "write_roots": [
        "knowledge"
      ],
      "source_read_roots": [
        "knowledge/observations",
        "knowledge/decisions"
      ],
      "targets": [
        {
          "id": "domain-transactions",
          "path": "standards/domain-transactions.md",
          "applicability": "Selected domain transaction boundary",
          "allowed_actors": [
            "architecture-owner"
          ],
          "adoption_source": {
            "root": "evidence/adoptions",
            "pointers": {
              "subject_sha256": "/subject_sha256",
              "target_id": "/target_id",
              "after_sha256": "/after_sha256",
              "actor": "/actor",
              "decision": "/decision",
              "decided_at": "/decided_at"
            }
          },
          "effect_source": {
            "root": "evidence/effect",
            "pointers": {
              "subject_sha256": "/subject_sha256",
              "target_id": "/target_id",
              "after_sha256": "/after_sha256",
              "adoption_sha256": "/adoption_sha256",
              "applicability": "/applicability",
              "state": "/state",
              "effective_at": "/effective_at"
            }
          }
        }
      ]
    }
  }
}
```

No Lesson/ADR package is needed at runtime. A selected source is attributed evidence;
its descriptor must match any JSON identity fields, but no foreign schema validation
or accepted status is inferred. The target is read-only to this tool.

## Query and propose

First query with explicit common roots/config, `operation: query` and
`text: domain transaction`. Review actual matches, partial diagnostics and digest.
If a new identity is appropriate, the request shape is:

```json
{
  "project_root": "/absolute/project",
  "package_root": "/absolute/installed/standards-promotion",
  "project_config": "collaboration.json",
  "operation": "propose",
  "text": "domain transaction",
  "decision": {
    "action": "new",
    "query_sha256": "<actual query digest>",
    "acknowledge_partial": false,
    "reason": "A distinct rule replacement after review."
  },
  "content": {
    "title": "Clarify domain transaction ownership",
    "target_id": "domain-transactions",
    "expected_target_sha256": "<actual existing rule raw sha256>",
    "replacement": "# Domain transaction ownership\n\nKeep one transaction-completion owner within the selected domain.\n",
    "rationale": "Limit the change to the evidenced transaction boundary.",
    "applicability": "Selected domain transaction boundary",
    "conflicts": [
      {
        "subject": "Unrelated domain persistence choices",
        "disposition": "preserve",
        "reason": "They are outside this proposal."
      }
    ],
    "sources": [
      {
        "path": "knowledge/observations/<actual lesson filename>",
        "expected_sha256": "<actual source raw sha256>",
        "kind": "lesson",
        "id": "<actual lesson id>",
        "schema_version": "2.0.0",
        "reason": "Relevant observed transaction behavior."
      }
    ]
  }
}
```

Inspect/render the actual stored proposal for full source snapshots, before/after
and computed subject. This does not edit the rule. The owner can separately review
and adopt the exact subject, edit the actual target, and declare effect through the
existing project process. None of those actions is performed by this tool.

## Read actual decisions, target bytes and effect

The adoption source maps proposal subject, target ID, after digest, allowed actor,
`decision: adopt` and actual decided_at. The effect source separately maps the same
subject/target/after, exact raw adoption-source digest, configured applicability,
`state: active` and actual effective_at. These are required facts, not sample proof.
Use real source files/digests when reconciling:

```json
{
  "project_root": "/absolute/project",
  "package_root": "/absolute/installed/standards-promotion",
  "project_config": "collaboration.json",
  "operation": "reconcile",
  "reference": {
    "role": "standards-promotion.record",
    "id": "promotion-<actual 32 lowercase hex digits>"
  },
  "expected_sha256": "<actual proposal record raw sha256>",
  "adoption_source": {
    "binding_id": "domain-transactions",
    "path": "evidence/adoptions/selected.json",
    "expected_sha256": "<actual adoption source raw sha256>"
  },
  "effect_source": {
    "binding_id": "domain-transactions",
    "path": "evidence/effect/selected.json",
    "expected_sha256": "<actual effect source raw sha256>"
  }
}
```

Adopted plus matching target plus matching active declaration can yield effective
with the disclosed project-local trust basis. If the rule drifts, preserve adopted
but report drifted and unresolved effect. Missing effect evidence leaves effect
unresolved; it does not remove observed adoption. A successful reconcile means the
observation was persisted, not that all dimensions succeeded.

Once adoption was ever observed, do not revise this proposal even after revocation.
A conflict fix needs a NEW proposal identity, actual new baseline/source evidence
and new matching adoption. Withdraw/supersede does not revert the actual rule.
Read [authority](authority.md) for the exact trust, chronology and failure limits.
