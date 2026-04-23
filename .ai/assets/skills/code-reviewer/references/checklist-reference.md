# Code Review Checklist Quick Reference (.NET)

## File Type Detection

```
Aggregate Root:
  - src/Domain/**/Aggregates/*.cs
  - Any class inheriting from AggregateRoot<TId>

Domain Event:
  - src/Domain/**/Events/*Events.cs
  - Records implementing IDomainEvent

Entity:
  - src/Domain/**/Entities/*.cs
  - Classes implementing IEntity<TId>

Value Object:
  - src/Domain/**/ValueObjects/*.cs
  - Records or immutable classes

Use Case (Command):
  - src/Application/**/UseCases/Commands/*.cs

Use Case (Query):
  - src/Application/**/UseCases/Queries/*.cs

Controller:
  - src/Api/Controllers/*.cs

Mapper:
  - src/Application/**/Ports/**/*Mapper.cs

Outbox Data:
  - src/Infrastructure/**/Outbox/*Data.cs

Test:
  - tests/**/*.cs
```

## Aggregate Pattern Detection

- Type hierarchy is primary.
- `.dev/project-config.yaml` is secondary.
- If type and config conflict, report a mismatch and use type hierarchy as final decision.

## Review Priorities

- Aggregate Root / Events: critical
- Entity: high
- Value Object: medium

## Key Rules Summary

- Event-sourced aggregate state is assigned only in `When(...)`.
- Domain events should be immutable records with required metadata.
- DI uses `IServiceCollection`; no attribute-based scanning.
- Tests use xUnit, no `BaseTestClass`, and NSubstitute for mocks.
- Query behavior must not be mixed into write repositories.
