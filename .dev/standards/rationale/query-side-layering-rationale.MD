# Query-side Layering Rationale

## Decision

Query side uses an Application query port implemented by an Infrastructure adapter.

An additional Application Query Service is optional and exists only for composition, reusable query policy, or non-trivial calculation.

## Simple Flow

```text
Application Query Boundary
  -> IQueryRepository-derived port
  -> Infrastructure adapter
  -> DTO / Read Model
```

This is sufficient when the query has one data source and the adapter can directly produce the required read model.

## Composed Flow

```text
Application Query Boundary
  -> Application Query Service
     -> Query Repository A
     -> Query Repository B
  -> DTO / Read Model
```

Use this only when Application-level orchestration adds real value.

## Why

### Preserve Clean Architecture

Application owns the port and query policy. Infrastructure owns DbContext, SQL, connection, provider, and mapping mechanics.

### Avoid pass-through layers

Requiring Query Repository + Query Service for every query adds indirection without behavior.

### Keep read models independent from Aggregates

Query ports return DTOs, read models, IDs, scalars, or pages. They do not rehydrate mutable Aggregates.

### Support command candidate selection safely

Query side may return candidate Aggregate IDs. Command-side Application logic must reload each Aggregate by identity and revalidate current invariant/state before mutation.

## Why not put query methods on Aggregate Repository

Methods such as `FindByStatus`, `Search`, reporting, paging, or DTO projection:

- mix read-model and Aggregate lifecycle responsibilities;
- force write adapters to support unrelated query shapes;
- make command-side code depend on stale read criteria;
- blur CQRS boundaries.

## Practical Rules

- Query Repository is a pure read port derived from `IQueryRepository`.
- Query Repository implementation is an Infrastructure adapter.
- Simple queries may use the port directly.
- Add Application Query Service only for composition/policy/calculation.
- Do not call Infrastructure adapters "Application Query Services".
- Do not return mutable Aggregate Roots from query side.
