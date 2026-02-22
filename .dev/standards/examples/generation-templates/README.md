# Generation Templates (.NET)

This folder contains full-module templates for AI-generated code in the
.NET CA/DDD/CQRS stack. Use these when generating complete features,
not just single-file examples.

## How This Differs from examples/[pattern]
- `examples/[pattern]/` = single pattern examples
- `generation-templates/` = multi-file, full module templates

## Template List

### aggregate-usecase-full.md
Full Aggregate + Use Case template:
- Value Objects (IDs)
- Domain Events + type mapping
- Aggregate root
- Use case interface + input DTO
- Service implementation
- Test references (xUnit + BDDfy)

### reactor-full.md
Reactor template:
- Reactor interface
- Handler implementation
- Wolverine configuration hooks
- Test references

### complex-aggregate-spec.md
YAML spec template for complex aggregates:
- Entity hierarchy
- Invariants and rules
- Events and commands
- Relationships and cardinality

### test-case-full.md
Full use case test template:
- Fixture-based DI
- BDDfy scenarios (Gherkin-style naming)
- Event capture guidance

### test-suites.md
How to define test groupings using xUnit traits and filters.

### local-utils.md
Shared utilities required in new projects:
- DateProvider (time control)
- InMemory infrastructure expectations (ezDDD .NET)

## Usage Tips

1. Replace placeholders consistently.
2. Keep naming aligned across files.
3. Validate compilation and tests after generation.
