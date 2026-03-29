# Command Sub-Agent Implementation Playbook

Use this delegated sub-agent role when the main agent needs a worker focused on command-side use case implementation.

## Mandatory References

- `.ai/assets/shared/common-rules.md`
- `.ai/assets/shared/architecture-config.md`
- `.ai/assets/shared/testing-strategy.md`

## Rules

- Use WolverineFx handlers for commands
- Use `CqrsOutput` equivalent or the current repository result pattern
- Repository dependencies come from DI; do not add custom repository interfaces
- Tests follow xUnit + BDDfy-style naming guidance and no `BaseTestClass`

## Output Structure

- `src/Application/<Aggregate>/UseCases/Commands/`

