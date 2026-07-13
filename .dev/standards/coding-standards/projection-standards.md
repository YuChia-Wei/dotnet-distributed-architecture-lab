# Projection and Query Repository Coding Standards (.NET)

This document defines CQRS read-side ports, adapters, optional Query Services, and provider-specific considerations.

## Core Rules

- The query side does not modify Domain state.
- The query side returns a DTO, read model, ID, scalar, or page, not a persistable Aggregate Root.
- A Query Repository is an Application outbound port; its implementation is an Infrastructure adapter.
- A simple Query does not require a pass-through Query Service.
- Provider-specific tracking, materialization, and model registration rules apply only to adapters that use that provider.

## Query Repository Port

Every query repository port must implement the canonical marker:

```csharp
public interface IQueryRepository
{
}
```

```csharp
public interface IProductQueryRepository : IQueryRepository
{
    Task<ProductDetailsDto?> FindDetailsAsync(
        ProductId id,
        CancellationToken cancellationToken = default);

    Task<IReadOnlyList<ProductId>> FindIdsByStatusAsync(
        ProductStatus status,
        CancellationToken cancellationToken = default);

    Task<PagedResult<ProductSummaryDto>> SearchAsync(
        ProductSearchCriteria criteria,
        CancellationToken cancellationToken = default);
}
```

Allowed:

- use-case/read-model-specific criteria;
- DTO/read model projection;
- identity lists, scalars, counts, and existence checks;
- paging, sorting, and filtering;
- EF Core, Dapper, SQL, or another read adapter.

Forbidden:

- `Save`, `Add`, `Update`, `Delete`, or `Remove`;
- `SaveChanges` or an equivalent persistence write;
- returning a mutable Aggregate Root or child Entity;
- Domain behavior;
- treating a Query Repository as an Aggregate persistence port.

## Query Application Flow

### Simple Query

The Application boundary may depend directly on a Query Repository:

```text
Application Query Boundary
  -> IProductQueryRepository
  -> Infrastructure Query Adapter
  -> DTO / Read Model
```

### Composed Query

Add an Application Query Service only in these cases:

- composing multiple Query Repositories;
- composing remote/read-cache sources;
- reusable query policy;
- calculation or orchestration beyond simple mapping.

```text
Application Query Boundary
  -> ProductQueryService
     -> IProductQueryRepository
     -> IInventoryQueryRepository
  -> DTO / Read Model
```

The Query Service implementation belongs in Application and must not depend directly on a DbContext, connection, or provider API.

When Infrastructure directly implements a Query Repository port, do not also name that adapter an Application Query Service.

## Candidate IDs for Aggregate Behavior

A Query Repository may first obtain Aggregate IDs that match read criteria:

```csharp
var ids = await productQueries.FindIdsByStatusAsync(
    ProductStatus.Expired,
    cancellationToken);
```

Application then reloads each Aggregate by identity, and each Aggregate revalidates its current state and invariants.

A Query result is a candidate snapshot and must not be treated directly as command-side truth.

## DTOs and Paging

Prefer immutable `record` types for DTOs:

```csharp
public sealed record ProductSummaryDto(
    string Id,
    string Name,
    string Status);
```

A paged result must explicitly include items and paging metadata:

```csharp
public sealed record PagedResult<T>(
    IReadOnlyList<T> Items,
    long TotalCount,
    int Page,
    int PageSize);
```

Do not require every Query Repository to provide paging; add it only when the use case needs it.

## Conditional EF Core Guidance

The following rules apply only to EF Core query adapters:

- Prefer direct projection for read-only queries.
- If the global tracking policy does not disable tracking, read-model queries should explicitly use `AsNoTracking()`.
- Aggregate command-side loads are not subject to this section's read-model tracking rules.
- Use an async terminal operator that matches cardinality:
  - collection: `ToListAsync`
  - zero-or-one: `SingleOrDefaultAsync` or `FirstOrDefaultAsync`
  - existence: `AnyAsync`
  - count: `CountAsync` / `LongCountAsync`
- Do not replace async execution with `ToList()`, `.Result`, or `.Wait()`.
- Avoid client-side evaluation and unnecessary entity materialization.
- Optimistic concurrency and command-side persistence do not belong in a Query Repository.

When an EF projection read model needs model registration validation, implement `IProjectionReadModel` or the target repository's equivalent marker.

## Conditional Dapper / SQL Guidance

- SQL must be parameterized.
- Mapping must cover required DTO/read-model fields.
- Large result sets must define paging, streaming, or bounded materialization.
- Query cancellation should be passed to the provider API.
- Use a transaction only when an explicit query consistency requirement needs it.

## Automated Validation Ownership

- Roslyn analyzer:
  - `IQueryRepository`-derived ports must not declare persistence write methods;
  - they must not return an Aggregate Root or child Entity;
  - projection services must not call provider write APIs.
- Configuration tests:
  - assembled model registration for EF read models.
- Tests / profiling / AI review:
  - query shape, N+1 behavior, index usage, tracking policy, mapping completeness, and performance.

Do not infer Query Repository semantics from filenames or grep results.

## Review Checklist

- [ ] The Query Repository implements `IQueryRepository`.
- [ ] The port is in Application and the adapter is in Infrastructure.
- [ ] It returns a DTO/read model/ID/scalar/page.
- [ ] It has no write methods or provider writes.
- [ ] A simple Query has no unnecessary pass-through Query Service.
- [ ] Candidate IDs are used to reload Aggregates and validate invariants in the command flow.
- [ ] Provider-specific async/materialization rules are correct.
- [ ] Large result sets have paging, streaming, or a bound.

## Related Documents

- [Repository Standards](repository-standards.md)
- [Use Case Standards](usecase-standards.md)
- [Query-side Layering Rationale](../rationale/query-side-layering-rationale.MD)
