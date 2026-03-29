# Reactor Test Sub-Agent Playbook

Use this delegated worker role when the main agent needs tests for event-driven reactors, asynchronous side effects, and integration boundaries.

## Mandatory References

- `.ai/assets/shared/testing-strategy.md`
- `.ai/assets/shared/common-rules.md`
- `.ai/assets/skills/bdd-gwt-test-designer/skill.yaml`

## Focus Areas

- event trigger and handler behavior
- downstream side effects
- asynchronous verification and retry-safe assertions

## Output Structure

- `src/tests/Application/<Aggregate>/Reactors/`

## Relationship To Top-Level Skill

- `bdd-gwt-test-designer` designs scenarios and assertion intent
- this sub-agent implements reactor-oriented test code

