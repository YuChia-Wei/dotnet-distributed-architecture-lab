# .NET DDD Wolverine Coding Standards

## Overview

This is the main coding-standards document for the .NET stack and consolidates the specialized coding rules.
It preserves the design intent of DDD, Clean Architecture, CQRS, and Event Sourcing.

**Technical scope**: .NET backend. Database, ORM, event store, broker, and package choices are determined by target-repository evidence; package documentation in this repository is conditional/reference guidance.

## Specialized Coding Standards

### 1. [Aggregate Standards](./coding-standards/aggregate-standards.md)
- Aggregate Root design and event-sourcing rules
- Domain Event lifecycle
- How to define Invariants and Contracts

### 2. [UseCase Standards](./coding-standards/usecase-standards.md)
- Command/Query separation
- Handler and transaction boundaries
- Input/Output DTO rules

### 3. [Controller Standards](./coding-standards/controller-standards.md)
- ASP.NET Core API design rules
- Request/Response handling
- Error handling and validation

### 4. [Repository Standards](./coding-standards/repository-standards.md)
- Aggregate Repository canonical/compatibility contract
- Pure Query Repository marker
- Conditional adapter guidance
- Outbox and consistency requirements

### 5. [Test Standards](./coding-standards/test-standards.md)
- xUnit + BDDfy default testing rules; GWT remains mandatory and 3A prohibited when the target team disables BDDfy
- NSubstitute mock usage rules
- Profile-based testing

### 6. [Projection Standards](./coding-standards/projection-standards.md)
- CQRS Read Model rules
- EF Core Projection and performance strategy

### 7. [Mapper Standards](./coding-standards/mapper-standards.md)
- DTO/Domain conversion rules
- Mapper class structure

### 8. [Archive Standards](./coding-standards/archive-standards.md)
- Archive Pattern and soft deletion
- Historical data tracking

### 9. [Reactor Standards](./coding-standards/reactor-standards.md)
- Reactor interface types and event-processing boundaries
- `DomainEventData` rules
- replay and duplicate-delivery considerations

### 10. [Profile / Environment Configuration Standards](./coding-standards/profile-configuration-standards.md)
- `DOTNET_ENVIRONMENT` / `ASPNETCORE_ENVIRONMENT` rules
- `appsettings.{Environment}.json` naming and override behavior
- InMemory/Outbox profile-specific DI constraints

## Core Design Principles

### 1. Domain-Driven Design (DDD)
- Keep Domain logic in the Domain layer
- Use Ubiquitous Language
- Clearly separate Bounded Contexts

### 2. Clean Architecture
- Direct dependencies from outer layers inward
- Keep the Domain layer framework-independent
- Port and Adapter pattern

### 3. CQRS
- Separate Commands from Queries
- Separate Read Models from Write Models

### 4. Event Sourcing
- Represent state changes primarily as events
- WolverineFx may be a target-selected event/message adapter; it is not a portable
  Application requirement

### 5. Testing Discipline
- Mutation Testing (Stryker.NET)
- Contract Testing (API/Message contracts)

## Implementation Rules

### ⚠ Code Style
- **Prefer `this.` usage**: Prefer `this.` when accessing members
- **Folder naming**: Use plural folder names within projects
- **XML documentation comments**: Public APIs must have XML summaries (written in Traditional Chinese using Taiwan terminology)

### ⚠ DTO Naming Rules

| Layer | Input naming | Output naming |
|------|-----------|------------|
| `<DomainName>.WebApi` | `*Request` | `*Response` |
| `<DomainName>.Applications` | `*Input` | `*Output` |

### ⚠ CQRS and Wolverine Rules

1. **Immutability**: Commands, Queries, and Events should be immutable (prefer `record`)
2. **Naming**: Use action-first names such as `CreateOrder` and `GetProduct`
3. **Handler principle**: Keep Handlers small and focused; use injected services instead of handling infrastructure details inside a Handler
4. **Idempotency**: Event handling must account for at-least-once delivery and check for duplicates before external I/O

### ⚠ Use Case and Optional Handler Placement Rules

| Type | Rule | File naming |
|------|------|---------|
| Use Case port | Transport-independent interface | `I<Operation>UseCase.cs` |
| Use Case implementation | Application orchestration | `<Operation>UseCase.cs` |
| Dispatch Handler | Create only for a real dispatch entry | `<Operation>CommandHandler.cs` |
| MQ Consumer Handler | Place in the Consumer/Presentation adapter | `<Event>Handler.cs` |

### ⚠ Event Placement Rules

| Event type | Location |
|-----------|---------|
| Domain Events | `./src/<Domain>/DomainCore/<DomainName>.Domains/DomainEvents` |
| Domain Event Handlers | `./src/<Domain>/DomainCore/<DomainName>.Applications/DomainEventHandlers` |
| Integration Event Handlers | `./src/<Domain>/Presentation/<DomainName>.Consumer/IntegrationEventHandlers` |
| Integration Event Schema | `./src/BC-Contracts/Lab.MessageSchemas.<Domain>` |

### ⚠ Repository and Query Port Rules

Portable Aggregate Repository：

```csharp
public interface IAggregateRepository<TAggregate, TId>
    where TAggregate : AggregateRoot<TId>
{
    Task<TAggregate?> FindByIdAsync(TId id, CancellationToken cancellationToken = default);
    Task SaveAsync(TAggregate aggregate, CancellationToken cancellationToken = default);
}
```

Compatibility：

```csharp
public interface IDomainRepository<TAggregate, TId>
    : IAggregateRepository<TAggregate, TId>
    where TAggregate : AggregateRoot<TId>
{
}
```

Core rules:

- A Repository root must be an Aggregate Root; child Entity repositories are prohibited.
- The shared Aggregate Repository exposes only `FindByIdAsync` and `SaveAsync`.
- Soft deletion is Aggregate behavior followed by `SaveAsync`.
- Physical purge uses a restricted capability port.
- Query ports must implement `IQueryRepository` and remain read-only.
- Simple Queries may use a Query Repository directly; add an Application Query Service only for composition, policy, or calculation.
- Database, ORM, event store, and package choices are determined by the target repository.
- Batch persistence is a target-specific opt-in pattern, not a portable default interface.
- A normal single-Aggregate Use Case does not inject `IUnitOfWork` by default; depend on it explicitly only for a clear strong-consistency requirement.
- Do not clear or acknowledge pending Domain Events before a successful commit.

Full rules:

- [Repository Standards](./coding-standards/repository-standards.md)
- [Projection Standards](./coding-standards/projection-standards.md)
- [Aggregate Repository Rationale](./rationale/generic-repository-only-rationale.MD)
- [Query-side Layering Rationale](./rationale/query-side-layering-rationale.MD)

### ⚠ Profile-Based Testing
- **Do not use BaseTestClass or BaseUseCaseTest as test base classes**
- All tests must support the `test-inmemory` and `test-outbox` profiles
- Control profiles with `appsettings.*.json`
- Follow [Profile / Environment Configuration Standards](./coding-standards/profile-configuration-standards.md) for profile naming, loading, DI branches, and profile-specific infrastructure rules

### ⚠ Outbox / Inbox Pattern
- A Use Case depends on a project-owned event-publisher port
- When the target repository selects WolverineFx, an Infrastructure adapter may use its Outbox mechanism for reliable event publication
- If an Inbox Pattern is introduced, the Consumer side should follow the same convention
- Transaction boundary: state changes during command handling must align with the persistence consistency strategy

## Automated Checks

```bash
# Transitional local orchestrator
.ai/scripts/check-all.sh

# Transitional spec helper
.ai/scripts/check-spec-compliance.sh <spec-file> <task-name>

# Mutation testing runner
.ai/scripts/check-mutation-coverage.sh
```

> `.ai/scripts` is currently a transitional AI workflow/orchestration area. C# semantic rules should gradually move to Roslyn Analyzers, `.editorconfig`, `dotnet format`, architecture tests, dotnet tests, or dotnet tools.

## Related Documents

- [Best Practices](./best-practices.md)
- [Anti-Patterns](./anti-patterns.md)
- [Legacy Todo/Wolverine profile example](./coding-guide.md) (not active product truth)
- [Code Review Checklist](./CODE-REVIEW-CHECKLIST.md)
