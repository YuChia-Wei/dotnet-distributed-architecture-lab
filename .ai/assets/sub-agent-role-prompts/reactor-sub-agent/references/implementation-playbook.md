# Reactor Sub-Agent Implementation Playbook

Use this delegated sub-agent role when the main agent needs a worker focused on reactor implementation for cross-aggregate consistency.

## Mandatory References

- `.ai/assets/shared/common-rules.md`
- `.ai/assets/shared/architecture-config.md`
- `.ai/assets/shared/testing-strategy.md`

## Rules

- Reactors handle event data, not domain entities
- Use WolverineFx message handlers for event processing
- Do not query another aggregate's repository directly; use query services

## Output Structure

- `src/Application/<Aggregate>/Reactors/`

