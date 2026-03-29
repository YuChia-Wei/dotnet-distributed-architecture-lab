# Aggregate Test Sub-Agent Playbook

Use this delegated worker role when the main agent needs aggregate-focused tests for invariants, event sourcing, and domain-event expectations.

## Mandatory References

- `.ai/assets/shared/testing-strategy.md`
- `.ai/assets/shared/common-rules.md`
- `.ai/assets/skills/bdd-gwt-test-designer/skill.yaml`

## Focus Areas

- aggregate state transition coverage
- invariant and postcondition coverage
- domain event publication and serialization-sensitive checks

## Output Structure

- `src/tests/Domain/<Aggregate>/`

## Relationship To Top-Level Skill

- `bdd-gwt-test-designer` supplies scenario intent
- this sub-agent turns that intent into aggregate-focused tests

