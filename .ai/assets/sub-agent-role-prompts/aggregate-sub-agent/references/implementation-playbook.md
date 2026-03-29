# Aggregate Sub-Agent Implementation Playbook

Use this delegated sub-agent role when the main agent needs a worker focused on DDD aggregate implementation.

## Mandatory References

- `.ai/assets/shared/common-rules.md`
- `.ai/assets/shared/architecture-config.md`
- `.ai/assets/shared/testing-strategy.md`
- `.ai/assets/shared/dto-conventions.md`
- `.ai/assets/shared/domain-rules.md`

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

