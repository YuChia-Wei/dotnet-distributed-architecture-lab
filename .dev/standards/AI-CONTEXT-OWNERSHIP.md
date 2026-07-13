# AI Context Rule Ownership

This standard assigns one normative owner to reusable AI-context rules and defines how secondary agent-loading surfaces consume them.

## Ownership Model

- `.dev/standards/` owns normative rule semantics, rule strength, applicability, and approved override slots.
- `.ai/assets/shared/` and `.ai/assets/tech-stacks/` are agent-loading projections. They may summarize a rule for execution, but must cite its rule ID and canonical standard.
- Skills own workflow behavior and output contracts, not the domain rules they consume.
- Runtime wrappers, checklists, examples, and workflow records are derived consumers and never become normative through repetition.
- `.dev/standards/AI-CONTEXT-OWNERSHIP.yaml` is the machine-readable registry. Add conflicted or cross-cutting rule families incrementally instead of attempting an unreviewed bulk migration.

## Rule Strength

| Strength | Meaning | Override policy |
| --- | --- | --- |
| `invariant` | Framework minimum that remains active for every adopting target. | Forbidden; a conflict must be reported as a waiver request. |
| `profile-default` | Default selected by an adopted profile. | May change only through explicit target-repository evidence. |
| `conditional` | Active only when its declared applicability predicate is satisfied. | Becomes not applicable when the predicate is false. |
| `example` | Illustrative material with no normative force. | Not applicable. |
| `historical` | Retained provenance that is not active guidance. | Not applicable. |

Do not use an unqualified `mandatory` or `default` when the applicable strength is not clear.

## Precedence

1. User approval and the applicable `AGENTS.md` procedural instructions.
2. Explicit target-repository facts and decisions for declared decision slots.
3. Framework `invariant` rules. Target conflicts are reported; they are not silent overrides.
4. Adopted `profile-default` rules.
5. Applicable `conditional` rules.
6. Derived `.ai` projections, runtime wrappers, and checklists.
7. Examples.
8. Historical records.

Target evidence may select technologies or replace a profile default. It cannot silently remove a framework invariant.

## Consumer Contract

Every registered derived consumer must:

- identify the canonical rule with `Rule IDs:` or an equivalent explicit source declaration;
- link to the canonical standard instead of independently redefining ownership;
- preserve the registered strength and applicability when it summarizes the rule;
- keep examples clearly illustrative.

The validator checks registry structure, paths, anchors, strength/override compatibility, and declared consumer references. Semantic parity remains a review responsibility.
