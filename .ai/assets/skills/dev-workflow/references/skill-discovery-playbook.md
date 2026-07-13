# Dev Workflow Skill Discovery Playbook

Use this playbook when the active repository may already have downstream skills, agents, prompts, or tools that can satisfy `dev-workflow` capability slots.

Discovery is allowed to infer candidates, but routing should prefer explicit declarations over natural-language guesses.

## Discovery Order

1. Read the active capability profile if one exists.
2. Inspect available skill registries and runtime wrappers.
3. Prefer structured metadata such as `capability_slots`, `inputs`, `outputs`, `triggers`, and `constraints`.
4. If metadata is missing, infer from skill name, description, trigger phrases, and documented outputs.
5. Assign a confidence level for each candidate.
6. Route automatically only when confidence is high or medium with no competing candidate.
7. Ask for user confirmation or use fallback-mode when confidence is low, conflicting, or absent.

## Metadata Contract

Downstream skills should declare capability slots when possible:

```yaml
name: "architecture-reviewer"
description: "Designs and reviews architecture decisions."
capability_slots:
  - "architecture"
  - "review"
inputs:
  - "requirements"
  - "existing architecture docs"
outputs:
  - "architecture findings"
  - "target decision"
```

`dev-workflow` should treat declared `capability_slots` as stronger evidence than title or description matches.

## Confidence Levels

| Confidence | Evidence | Action |
| --- | --- | --- |
| High | Skill explicitly declares matching `capability_slots`, or the active profile maps the slot to the skill. | Route directly and record the mapping source. |
| Medium | Name, description, triggers, inputs, and outputs clearly match exactly one capability slot with no strong competing candidate. | Route and mark the mapping as inferred. |
| Low | Multiple candidates match, the description is broad, or the candidate spans several capabilities without clear priority. | List candidates and ask for user confirmation before routing. |
| None | No candidate or evidence is available. | Use fallback-mode and record the missing capability. |

## Heuristic Hints

Use these hints only when structured metadata is unavailable.

| Signals | Likely capability slot |
| --- | --- |
| requirement, user story, stakeholder input, acceptance need | `requirements` |
| spec, behavior contract, acceptance criteria, JSON spec | `specification` |
| problem frame, CBF, SWF, phenomena, workpiece | `problem-framing` |
| architecture, DDD, Clean Architecture, CQRS, bounded context, aggregate, port, adapter | `architecture` |
| BDD, GWT, Given-When-Then, scenario, assertion | `test-design` |
| implement, command handler, query handler, reactor, use case | `implementation` |
| refactor, staged change, extract, rename, local cleanup | `refactoring` |
| review, findings, severity, risk, checklist | `review` |
| compliance, coverage gate, validator, pass/fail | `compliance-validation` |

## Conflict Rules

- If a local profile and discovered metadata disagree, prefer the active profile and report the mismatch.
- If two skills have high confidence for the same slot, choose the more specific skill.
- If one skill claims many slots and another claims one exact slot, prefer the exact-slot skill for that stage.
- If the selected skill is a review or validation skill, do not use it as an implementation skill.
- If the selected skill is a workflow skill, do not use it as a domain specialist.
- If the requested work is AI context maintenance, documentation-only governance, or repository initialization, stop dev-workflow discovery and route to the owning non-development skill.

## Discovery Output

When discovery affects routing, include:

```text
Skill Discovery:
- Capability: <slot>
- Selected: <skill or fallback-mode>
- Confidence: high | medium | low | none
- Evidence: <profile mapping, metadata field, or inferred signal>
- Alternatives: <other candidates or none>
- User Decision Needed: yes | no
```

## Fallback Trigger

Use `fallback-playbooks.md` when:

- no candidate is found;
- confidence is low and the user has not confirmed a candidate;
- the only candidate is too broad for the stage;
- the required specialist skill is unavailable in the current runtime;
- the candidate would violate its own constraints if used for the stage.
