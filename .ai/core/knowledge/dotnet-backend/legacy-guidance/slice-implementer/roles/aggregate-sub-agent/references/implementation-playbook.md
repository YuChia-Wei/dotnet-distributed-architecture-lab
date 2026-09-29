# Aggregate Sub-Agent Implementation Playbook

Reference-only technical guidance. Apply the target-selected architecture and technology;
this projection neither activates a runtime role nor creates an additional normative owner.

Technical reference for DDD aggregate implementation. Loading this material does not dispatch a worker.

## Mandatory References

- `../../../../../shared/common-rules.md`
- `../../../../../shared/architecture-config.md`
- `../../../../../shared/testing-strategy.md`
- `../../../../../shared/dto-conventions.md`
- `../../../../../shared/domain-rules.md`

## Critical Rules

- Aggregate state changes only via event application
- Constructors must not directly set state
- Events are immutable and carry metadata
- Use contract-style validation for aggregate and entities
- Value Objects use repository-standard guard patterns

## Output Requirements

- Aggregate Root
- Domain Events
- Value Objects
- Entities if any
- Contract validations

## Output Structure

- `src/Domain/<Aggregate>/`
