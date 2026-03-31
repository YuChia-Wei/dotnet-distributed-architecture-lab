# Examples Index

This index lists the reusable examples under `.dev/standards/examples/` without tying them to any source-stack migration history.

## Principles

- examples should be understandable on their own
- examples should demonstrate current architectural rules and implementation patterns
- example indexes should not depend on Java -> .NET conversion notes

## Categories

### Aggregate Examples

- `examples/aggregate/`
  - aggregate roots, ids, events, and value-object style patterns

### ASP.NET Core / Runtime Examples

- `examples/aspnet-core/`
  - Program setup, DI, configuration, and environment/profile examples

### BDD / Test Examples

- `examples/bdd-given-when-then-example/`
  - scenario-driven test examples
- `examples/bdd-gherkin-example/`
  - Gherkin-oriented reference examples
- `examples/bdd-gherkin-test/`
  - end-to-end BDD-style test examples
- `examples/test/`
  - fixture-based and use-case-oriented tests

### Controller / API Examples

- `examples/controller/`
  - controller and request/response handling patterns

### DTO / Mapper Examples

- `examples/dto/`
  - DTO design examples
- `examples/mapper/`
  - mapping examples between domain and data/DTO layers

### Outbox / Persistence Examples

- `examples/outbox/`
  - outbox data, mapper, and persistence examples
- `examples/projection/`
  - read-model and projection examples
- `examples/inquiry-archive/`
  - query/archive style examples

### Generation Templates

- `examples/generation-templates/`
  - generation-oriented templates and local utilities

### Use Case Examples

- `examples/usecase/`
  - application/use-case examples and supporting service patterns

## Maintenance Notes

- If a new example folder is added, register it here by category.
- Keep this file category-oriented rather than file-by-file when possible.
- If a specific file needs emphasis, mention it in the folder README instead of rebuilding a migration matrix here.
