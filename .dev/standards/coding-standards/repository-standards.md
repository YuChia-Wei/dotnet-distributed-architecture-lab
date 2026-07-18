# Repository Coding Standards (.NET)

This document is the canonical standard for aggregate persistence and query-side data access.

This standard defines application-port semantics without prescribing a database, ORM, event store, or package. EF Core, Dapper, Npgsql, and other adapter content is conditional implementation guidance only.

## Core Boundaries

Repository rules distinguish three roles:

| Role | Purpose | May modify data | Primary return type |
| --- | --- | --- | --- |
| Aggregate Repository | Rehydrate and persist an Aggregate Root | Yes | Aggregate Root |
| Query Repository | Read-only access to read models | No | DTO, read model, ID, scalar, or page |
| Capability-specific Writer | Explicit capabilities such as outbox, projection, import, or purge | Yes | Capability-defined; never an Aggregate |

A repository interface is an Application outbound port. EF Core, Dapper, SQL, event-store, file, or remote-persistence implementations are Infrastructure outbound adapters.

## Aggregate Repository

### Canonical Contract

```csharp
public interface IAggregateRepository<TAggregate, TId>
    where TAggregate : IAggregateRoot<TId>
{
    Task<TAggregate?> FindByIdAsync(
        TId id,
        CancellationToken cancellationToken = default);

    Task SaveAsync(
        TAggregate aggregate,
        CancellationToken cancellationToken = default);
}
```

Rules:

- `TAggregate` MUST be an Aggregate Root.
- A child Entity MUST NOT have a Repository independently injectable by the Application.
- `FindByIdAsync` loads only by Aggregate identity.
- `SaveAsync` means "persist an Aggregate whose domain behavior has completed."
- An adapter may use insert, update, upsert, tracked persistence, or event append as appropriate.
- A Repository MUST NOT contain status, name, filter, paging, or DTO query methods.
- A Repository MUST NOT execute domain behavior itself.
- A Repository MUST NOT clear pending Domain Events before persistence succeeds.

### Compatibility Contract

Existing products may already use `IDomainRepository` for an Aggregate Repository. This compatibility contract is retained to avoid needless migration noise when adopting this context:

```csharp
public interface IDomainRepository<TAggregate, TId>
    : IAggregateRepository<TAggregate, TId>
    where TAggregate : IAggregateRoot<TId>
{
}
```

Rules:

- New code SHOULD prefer `IAggregateRepository<TAggregate, TId>`.
- `IDomainRepository<TAggregate, TId>` is not a second repository model.
- Every Aggregate Root constraint still applies to the compatibility contract.
- `IDomainRepository<ChildEntity, TId>` is a violation and MUST NOT be excused for compatibility.
- An aggregate-specific interface is permitted only for compatibility or as an explicit type alias; it MUST NOT add methods beyond the shared contract.
- A meaningless empty interface created only for renaming is forbidden.

## Forbidden Generic Write Interfaces

Application code MUST NOT depend on a public CRUD abstraction accepting arbitrary Entities or table models, such as:

- `IRepository<TEntity, TId>`
- `IGenericRepository<TEntity, TId>`
- `IWritableRepository<TEntity, TId>`
- `ICrudRepository<TEntity, TId>`

Infrastructure adapters may internally use private/internal DAOs, table gateways, or persistence helpers, but MUST NOT expose them directly as Application ports.

## Query Repository

### Marker

```csharp
public interface IQueryRepository
{
}
```

A query-specific port MUST implement the marker:

```csharp
public interface IProductQueryRepository : IQueryRepository
{
    Task<ProductDetailsDto?> FindDetailsAsync(
        ProductId id,
        CancellationToken cancellationToken = default);

    Task<IReadOnlyList<ProductId>> FindIdsByStatusAsync(
        ProductStatus status,
        CancellationToken cancellationToken = default);
}
```

Rules:

- A Query Repository is a read-only port.
- It may return a DTO, read model, ID, scalar, or page.
- Returning an Aggregate Root or child Entity that can be modified and saved is forbidden.
- `Save`, `Add`, `Update`, `Delete`, `Remove`, and equivalent persistence writes are forbidden.
- Query criteria may follow the use case/read model and need not imitate an Aggregate Repository.
- Query Repository implementations belong in Infrastructure.

### Optional Query Service

A simple Query may depend directly on a Query Repository at the Application boundary.

Add an Application Query Service only when it:

- combines multiple Query Repositories or external read sources;
- contains a reusable query policy; or
- performs calculation or orchestration beyond simple mapping.

Do not require a pass-through Query Service for every Query.

## Delete and Purge

### Soft delete

Soft delete is Aggregate behavior:

```csharp
aggregate.Delete(actorId, reason);
await repository.SaveAsync(aggregate, cancellationToken);
```

A Repository SHOULD NOT replace an Aggregate deletion invariant with physical row deletion.

### Physical purge

Physical deletion uses a separate, restricted capability port and does not belong in the shared Aggregate Repository:

```csharp
public interface IAggregatePurgePort<TAggregate, TId>
    where TAggregate : IAggregateRoot<TId>
{
    Task PurgeAsync(
        TId id,
        CancellationToken cancellationToken = default);
}
```

A Purge Use Case MUST first address:

- authorization;
- retention policy;
- legal/audit constraints;
- Aggregate eligibility; and
- related outbox/archive/attachment cleanup policy.

## Transactions and Unit of Work

Eventual consistency is the default for cross-Aggregate coordination.

A normal single-Aggregate Use Case does not automatically inject `IUnitOfWork` merely because it uses a Repository.

Depend on it explicitly only when a Use Case requires multiple persistence participants to commit or roll back together:

```csharp
public interface IUnitOfWork
{
    Task CommitAsync(CancellationToken cancellationToken = default);
}
```

Rules:

- The explicit dependency communicates an exceptional strong-consistency requirement.
- A Repository participating in an external Unit of Work MUST NOT commit independently.
- Repository-owned independent commits MUST NOT break Aggregate + Outbox atomicity.
- Transaction middleware/decorators may implement mechanics but MUST NOT hide the strong-consistency dependency declared by the Use Case.

Domain Event lifecycle:

1. Execute Use Case orchestration and Aggregate behavior.
2. Obtain pending Domain Events.
3. Atomically persist Aggregate state/events and required Outbox records.
4. Commit。
5. Acknowledge/clear pending events only after a successful commit.
6. Preserve retry and optimistic-concurrency semantics on failure.

## Target-specific Aggregate Batch Capability

Portable building blocks do not publish a mandatory `IAggregateBatchRepository`.

A target repository may define a batch port only when supported by measured evidence, for example:

```csharp
public interface IProductAggregateBatchPort
{
    Task<IReadOnlyList<ProductAggregate>> FindByIdsAsync(
        IReadOnlyCollection<ProductId> ids,
        CancellationToken cancellationToken = default);

    Task SaveAllAsync(
        IReadOnlyCollection<ProductAggregate> aggregates,
        CancellationToken cancellationToken = default);
}
```

Enabling conditions:

- expected cardinality is actually greater than one;
- N+1 IO, latency, or throughput problems have been measured;
- the adapter can provide effective batch optimization;
- missing/duplicate IDs, ordering, and maximum batch size are defined;
- optimistic concurrency, partial failure, retry, and resume are defined;
- pending-event and Outbox semantics are defined for each Aggregate; and
- the batch port is excluded from default templates, default DI, and ordinary Use Cases.

The batch port:

- does not inherit `IAggregateRepository<TAggregate, TId>`;
- accepts only Aggregate Roots;
- keeps `FindByIdsAsync` identity-based;
- does not allow status/filter queries; and
- MUST NOT replace executing Aggregate behavior individually.

`IUnitOfWork` determines the all-or-nothing business transaction; batch methods determine only the IO shape.

Bulk work defaults to bounded chunks, retry, and resumable progress. A single long transaction over an unbounded collection is forbidden.

Imports, migrations, projection rebuilds, or purges that do not execute normal Aggregate behavior SHOULD use a capability-specific writer rather than an Aggregate batch port.

## Conditional Adapter Guidance

### EF Core

- Query/read-model flows SHOULD use `AsNoTracking` or direct projection according to the tracking policy.
- Whether Aggregate loads are tracked depends on the adapter's direct domain mapping, persistence-model mapping, or tracked-aggregate strategy.
- Use a cardinality-appropriate async terminal operator such as `ToListAsync`, `SingleOrDefaultAsync`, `FirstOrDefaultAsync`, `AnyAsync`, or `CountAsync`.
- Sync-over-async is forbidden.
- Optimistic concurrency MUST have explicit token/version mapping and conflict handling.
- Domain Events MUST NOT be cleared before `SaveChangesAsync` succeeds.

### Dapper / direct SQL

- Connection/transaction lifetime MUST align with the Unit of Work or adapter atomic operation.
- Update/delete SQL MUST check an optimistic-concurrency version or equivalent condition.
- Multi-statement Aggregate persistence and Outbox writes MUST share an atomic boundary.
- Tests and review verify mapping completeness.

### Event store

- Append MUST include an expected version or equivalent concurrency condition.
- Append only pending events.
- Mark events committed only after append/commit succeeds.
- A snapshot is an optimization and MUST NOT replace the event stream as source of truth.

## Automated Validation Ownership

Repository semantic diagnostics use Roslyn symbol/type analysis; filenames or grep are not CI authority.

Validation MUST cover:

- the canonical `IAggregateRepository<,>` generic argument is an Aggregate Root;
- compatibility `IDomainRepository<,>` and every derived interface follow the same rules;
- the shared Aggregate Repository method surface contains only `FindByIdAsync` and `SaveAsync`;
- ports marked as Query Repositories contain no writes or mutable domain return types;
- a child Entity cannot be a repository root; and
- default severity for violations is `error`.

The target repository enables analyzer/architecture-test rules for target-specific batch ports through a local marker. The portable analyzer does not depend on an unfinished Use Case/Handler taxonomy.

## Review Checklist

### Aggregate Repository

- [ ] Uses `IAggregateRepository<TAggregate, TId>` or compatible `IDomainRepository<TAggregate, TId>`.
- [ ] `TAggregate` is an Aggregate Root.
- [ ] The shared contract contains only `FindByIdAsync` and `SaveAsync`.
- [ ] No child Entity repository exists.
- [ ] No DTO/filter/paging query methods exist.
- [ ] The Repository does not execute domain behavior.

### Query Repository

- [ ] Implements the `IQueryRepository` marker.
- [ ] Returns only read-side types, IDs, or scalars.
- [ ] Contains no persistence writes.
- [ ] A simple Query has no needless pass-through Query Service.

### Transaction / Events

- [ ] `IUnitOfWork` is used only for an explicit strong-consistency Use Case.
- [ ] A Repository does not commit independently while participating in a Unit of Work.
- [ ] Atomicity of Aggregate state/events and Outbox is defined.
- [ ] Pending events are cleared/acknowledged only after commit succeeds.

### Optional Batch

- [ ] The target repository has measured evidence and explicit batch semantics.
- [ ] The batch port is absent from the portable/default contract.
- [ ] Bulk work uses bounded chunks.
- [ ] Partial failure, retry, concurrency, and event/outbox behavior are defined.

## Related Documents

- [Aggregate Standards](aggregate-standards.md)
- [Projection Standards](projection-standards.md)
- [Use Case Standards](usecase-standards.md)
- [Generic Repository Rationale](../rationale/generic-repository-only-rationale.MD)
- [Query-side Layering Rationale](../rationale/query-side-layering-rationale.MD)
