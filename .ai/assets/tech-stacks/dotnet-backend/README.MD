# .NET Backend AI Context

This profile contains agent-facing context for .NET backend projects.

## Scope

Included:

- DDD, Clean Architecture, CQRS, and Hexagonal Architecture backend rules
- ASP.NET Core backend host configuration
- command, query, reactor, aggregate, repository, projection, and controller patterns
- Dapper, EF Core, PostgreSQL, WolverineFx, RabbitMQ, Kafka, Outbox, and Event Sourcing guidance
- xUnit Given-When-Then testing rules, with BDDfy and NSubstitute as overridable profile defaults and optional `.feature` support

Excluded:

- Razor
- Blazor
- MAUI
- ASP.NET MVC view rendering
- frontend UI component generation
- full-stack or mono-system template rules

## Structure

```text
.ai/assets/tech-stacks/dotnet-backend/
  references/
  shared/
```

## References

- `references/BUILDING-BLOCKS-CLASS-INDEX.MD`
- [BuildingBlocks reconstruction contract](../../../../.dev/standards/BUILDING-BLOCKS-RECONSTRUCTION-CONTRACT.md)
- `references/CODE-REVIEW-INDEX.MD`
- `source-includes/domain/` - optional interface-first Domain contracts and the
  executable-tested `EsAggregateRoot<TId>` source include
- `references/CODE-TEMPLATES.MD`
- `references/COMMON-PITFALLS.MD`
- `references/FAILURE-CASES.MD`

## Current Shared Materials

- `shared/architecture-config.md`
- `shared/code-review-checklist.md`
- `shared/common-rules.md`
- `shared/domain-rules.md`
- `shared/dto-conventions.md`
- `shared/testing-strategy.md` (active projection; `shared/testing-standards.md` is a compatibility entry)
- `shared/testing-strategy.md`

## Boundary Rule

If a rule can be reused outside .NET backend repositories, keep it under `.ai/assets/shared/`. If it depends on .NET backend architecture, packages, testing tools, or host conventions, keep it under this profile.
