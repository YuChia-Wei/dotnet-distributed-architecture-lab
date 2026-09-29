# Reactor Sub-Agent Implementation Playbook

Reference-only technical guidance. Apply the target-selected architecture and technology;
this projection neither activates a runtime role nor creates an additional normative owner.

Technical reference for reactor implementation for cross-aggregate consistency. Loading this material does not dispatch a worker.

## Mandatory References

- `../../../../../shared/common-rules.md`
- `../../../../../shared/architecture-config.md`
- `../../../../../shared/testing-strategy.md`

## Rules

- Reactors handle event data, not domain entities
- Use WolverineFx message handlers for event processing
- Do not query another aggregate's write repository directly; use a read-only
  `IQueryRepository` port or an established QueryService when composition or policy
  requires one

## Output Structure

- `src/Application/<Aggregate>/Reactors/`
