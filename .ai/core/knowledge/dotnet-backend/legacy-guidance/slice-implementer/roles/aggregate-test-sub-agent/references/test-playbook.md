# Aggregate Test Sub-Agent Playbook

Reference-only technical guidance. Apply the target-selected architecture and technology;
this projection neither activates a runtime role nor creates an additional normative owner.

Technical reference for aggregate-focused tests of invariants, event sourcing and domain events. Loading it does not dispatch a worker.

## Mandatory References

- `../../../../../shared/testing-strategy.md`
- `../../../../../shared/common-rules.md`
- `target-authority:ai-assets-skills-bdd-gwt-test-designer-skill.yaml`

## Focus Areas

- aggregate state transition coverage
- invariant and postcondition coverage
- domain event publication and serialization-sensitive checks

## Output Structure

- `src/tests/Domain/<Aggregate>/`

## Relationship To Top-Level Skill

- `bdd-gwt-test-designer` supplies scenario intent
- this sub-agent turns that intent into aggregate-focused tests
