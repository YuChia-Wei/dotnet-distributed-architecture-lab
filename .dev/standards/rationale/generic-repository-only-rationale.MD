# Aggregate Repository Contract Rationale

## Decision

Portable command-side persistence uses:

```text
IAggregateRepository<TAggregate, TId>
  FindByIdAsync
  SaveAsync
```

`TAggregate` must be an Aggregate Root.

For migration compatibility:

```text
IDomainRepository<TAggregate, TId>
  extends IAggregateRepository<TAggregate, TId>
```

New code prefers `IAggregateRepository`.

## Why

### Preserve the Aggregate boundary

Repository persistence applies to an Aggregate Root consistency boundary. Child Entities are loaded and persisted through their owning Aggregate Root.

### Avoid general-purpose CRUD

`IRepository<TEntity, TId>`-style abstractions make it easy to persist arbitrary Entities or table models and bypass domain invariants.

### Keep the portable contract adapter-neutral

Tracked ORM, direct SQL, document stores, and event stores have different insert/update/append mechanics. `SaveAsync` expresses persistence intent without forcing one mechanism.

### Apply Interface Segregation

Batch loading/persistence, physical purge, read-model query, outbox, projection, and import are separate capabilities. Not every adapter or target repo needs them.

## Why keep `IDomainRepository`

Existing products may already use `IDomainRepository` for valid Aggregate repositories.

Keeping it as a compatibility contract:

- reduces migration noise;
- lets analyzers inspect existing repositories immediately;
- prevents valid legacy naming from hiding actual child-Entity repository violations.

Compatibility is not an exemption. The generic argument must still be an Aggregate Root.

## Why batch methods are not portable defaults

Some target systems need efficient identity-based loading and persistence of multiple instances of the same Aggregate type.

That requirement does not prove every repository needs:

- `FindByIdsAsync`;
- `SaveAllAsync`.

Portable standards therefore document a target-specific batch capability pattern but do not publish a mandatory batch interface.

Target opt-in requires measured IO need plus explicit chunking, concurrency, failure, event, outbox, and transaction semantics.

## Why purge is separate

Soft delete is Aggregate behavior followed by `SaveAsync`.

Physical purge has retention, authorization, legal, audit, and cleanup implications. It belongs to a restricted capability port rather than the normal Aggregate Repository.

## Practical Rules

- Aggregate write side: `IAggregateRepository<TAggregate, TId>`.
- Legacy compatibility: `IDomainRepository<TAggregate, TId>`.
- Query side: ports derived from `IQueryRepository`.
- Physical deletion: restricted purge port.
- Batch IO: target-specific opt-in capability.
- Technical writes: capability-specific writer.
- No public generic CRUD repository for arbitrary Entities.
