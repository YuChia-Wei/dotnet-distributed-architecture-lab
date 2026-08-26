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
  engineering-rule-catalog.yaml
  examples/
  references/
  shared/
  standards/
  templates/
  tooling/
    on-demand-mechanical-validation/
```

## References

- `references/BUILDING-BLOCKS-CLASS-INDEX.MD`
- [BuildingBlocks reconstruction contract](standards/BUILDING-BLOCKS-RECONSTRUCTION-CONTRACT.md)
- [Code Reviewer file-type and finding routing](../../skills/code-reviewer/references/review-routing.yaml)
- `references/CODE-REVIEW-INDEX.MD` - `v0.13.x` compatibility entry only
- `examples/` - canonical .NET backend profile example landing path
- `source-includes/domain/` - optional interface-first Domain contracts and the
  reference-only `EsAggregateRoot<TId>` source include; adopting targets own compilation and behavior evidence
- `references/CODE-TEMPLATES.MD`
- `references/COMMON-PITFALLS.MD`
- `references/FAILURE-CASES.MD`
- `tooling/on-demand-mechanical-validation/` - reference-only DBA mapping and
  target-owned analyzer/configuration-test creation recipes; no provider, project, or SDK is supplied

## Current Shared Materials

- `shared/architecture-config.md`
- `shared/code-review-checklist.md` (`v0.13.x` compatibility entry only)
- `shared/common-rules.md`
- `shared/domain-rules.md`
- `shared/dto-conventions.md`
- `shared/testing-strategy.md` (active projection; `shared/testing-standards.md` is a compatibility entry)

## Rule Resolution

`engineering-rule-catalog.yaml` is a resolver-ready exact projection of the
registered profile rule sections. The Markdown file and anchor recorded by a
catalog record remain the semantic owner. The catalog retains stable IDs,
selectors, full normative text, and hashes so task-scoped packet generation
does not scan this profile tree. Migrated profile-baseline documents without a
stable registered rule ID remain `identity-allocation-required` and are not
packet candidates.

## Boundary Rule

If a rule can be reused outside .NET backend repositories, keep it under `.ai/assets/shared/`. If it depends on .NET backend architecture, packages, testing tools, or host conventions, keep it under this profile.
