# Reactor Sub-Agent Implementation Playbook

Use this delegated sub-agent role when the main agent needs a worker focused on reactor implementation for cross-aggregate consistency.

## Mandatory References

- `.ai/assets/tech-stacks/dotnet-backend/shared/common-rules.md`
- `.ai/assets/tech-stacks/dotnet-backend/shared/architecture-config.md`
- `.ai/assets/tech-stacks/dotnet-backend/shared/testing-strategy.md`

## Rules

- Reactors handle event data, not domain entities
- Use WolverineFx message handlers for event processing
- Do not query another aggregate's write repository directly; use a read-only
  `IQueryRepository` port or an established QueryService when composition or policy
  requires one

## Output Structure

- `src/Application/<Aggregate>/Reactors/`

