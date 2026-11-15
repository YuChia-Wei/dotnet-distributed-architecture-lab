# Projection and Query Repository Coding Standards (.NET)

This document defines CQRS read-side ports, adapters, optional Query Services, and provider-specific considerations.

Here, query-side means the read operation. A read-model projector may separately
update its owned read store under an explicit event/failure contract; that is
not permission for a query reader to write, mutate the command store or perform
arbitrary external effects. See [role rationale](../../references/policy-rationale.md#query-reader-and-read-model-projector).

## Core Rules

- The query side does not modify Domain state.
- The query side returns a DTO, read model, ID, scalar, or page, not a persistable Aggregate Root.
- A Query Repository is an Application outbound port; its implementation is an Infrastructure adapter.
- A simple Query does not require a pass-through Query Service.
- Provider-specific tracking, materialization, and model registration rules apply only to adapters that use that provider.

Normalize a filter sentinel such as `all` before invoking the read port only
where the input contract defines that meaning. Keep results immutable where
the target needs isolated read state. For query-store writes, use the explicit
projector or [Archive boundary](archive-standards.md).

## Query Repository Port

Map the query-reader role and its dependencies explicitly. A target may use the
following marker, its own equivalent contract or a verified role mapping; the
canonical marker is not mandatory. Do not classify a projector as a query reader
merely because its name contains `Projection`.

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

- Target-selected Roslyn analyzer or architecture test:
  - recognized query-reader ports must not declare persistence write methods;
  - they must not return an Aggregate Root or child Entity;
  - query-reader services/adapters must not call provider write APIs.
- Target-owned configuration tests:
  - assembled model registration for EF read models.
- Tests / profiling / AI review:
  - query shape, N+1 behavior, index usage, tracking policy, mapping completeness, and performance.

Do not infer Query Repository semantics from filenames or grep results.

## Event-Driven Read-Model Projector

A projector consumes events and writes its owned read-model store through a
capability-specific writer. An ES projection is an event-driven materialization;
a DTO projection is a conversion/query expression; a query port reads results.
They do not acquire each other's capabilities from the word `Projection`.

| Role / example | Judgment |
|---|---|
| Reader: query DTOs through a read port | Allowed; no command-state mutation or writes hidden in the query. |
| Reader: call `SaveChanges` or update a read row while answering a query | Rejected under the query-only contract. |
| Projector: handle `ProductRenamed` and update its product-summary row | Allowed under the selected event and owned read-store contract. |
| Projector: load/save an Aggregate, change the command store or publish externally | Not authorized by read-store projection; requires a separately selected responsibility/contract. |

Select persistence, ordering and delivery semantics explicitly. The following
original pseudocode selects a local transaction containing both read-row update
and deduplication by `(projector version, event ID)`. The broker acknowledgement
is separate and occurs only after that transaction commits:

```text
receive event
validate supported envelope/schema and required data
begin owned read-store transaction
  if event ID already recorded for this projector version: no-op
  otherwise:
    require the expected per-stream sequence (gap -> rollback and retry/park)
    update owned read row
    record event ID and applied stream sequence in the same transaction
commit read-store transaction
ack delivery
```

This example assumes ordered per-stream processing; it supplies no global order.
It does not use timestamps to guess order or skip sequence gaps. Select a bounded
retry/parking and owner repair policy for poison data. A projector rebuild uses
a separately identified projection version/store and a selected replay/cutover
procedure; do not erase live checkpoints or acknowledge unread events.

| Selected case | Outcome and recovery |
|---|---|
| Duplicate after successful commit, including an ack timeout | Deduplication makes the read-store operation a no-op; retry acknowledgement. No exactly-once claim. |
| Read-row update or local commit fails | No ack and no completed checkpoint; roll back the transaction and retry the same event under the failure policy. |
| Separate ack fails or its result is unknown after commit | Read update remains committed; expect redelivery and deduplicate. Do not undo/reapply blindly or claim delivery completion. |
| Polling runner uses a checkpoint instead of broker ack | Advance checkpoint only after durable projection success. If separately stored checkpoint fails/is unknown, reread it and replay idempotently; never advance past an unprocessed gap. |
| Read row and checkpoint share a supported transaction | Commit them atomically; failure leaves neither completed. Transaction support must be proven by the adapter. |
| Unsupported event version / malformed required field | No success or checkpoint advance; park/retry with identifiable stream/event/version and data-owner repair. No silent defaults. |

Deduplication state must outlive the selected redelivery/replay window. Competing
projectors require transaction/concurrency protection for both rows and markers;
a standalone `HasSeen` check is insufficient. A scalar polling checkpoint covers
only a contiguous completed prefix, not the highest out-of-order event observed.
These are selected recovery examples, not a new event store, runner, broker or
cross-store atomicity service. Official basis and interpretation are recorded in
[policy rationale](../../references/policy-rationale.md#reconstruction-and-projection-sources).

## Review Checklist

- [ ] Reader/projector role and narrow dependencies are explicit through the
      target-selected contract or mapping; no mandatory canonical marker.
- [ ] The port is in Application and the adapter is in Infrastructure.
- [ ] It returns a DTO/read model/ID/scalar/page.
- [ ] It has no write methods or provider writes.
- [ ] A simple Query has no unnecessary pass-through Query Service.
- [ ] Candidate IDs are used to reload Aggregates and validate invariants in the command flow.
- [ ] Provider-specific async/materialization rules are correct.
- [ ] Large result sets have paging, streaming, or a bound.
- [ ] A projector writes only its owned read store; query DTO projection is distinct.
- [ ] Projector cases cover duplicate delivery, gaps, read-write/commit failure
      and checkpoint/ack failure; no completion before durable success.
- [ ] Concurrency, deduplication retention, poison-event repair and any replay
      cutover are selected; no unsupported exactly-once guarantee.

## Related Documents

- [Repository Standards](repository-standards.md)
- [Use Case Standards](../../architecture/ddd-cqrs/usecase-standards.md)
- [Query-side Layering Rationale](../../references/policy-rationale.md)
