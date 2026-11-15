# BuildingBlocks Reconstruction Contract

## Purpose

This document defines the minimum portable knowledge needed to reconstruct the
dotnet-backend BuildingBlocks boundary without copying a historical product.
The goal is architectural equivalence, not identical projects, namespaces, or
source code.

BuildingBlocks contains business-neutral contracts and narrowly justified
mechanical behavior. Product Domain and Application projects own business
semantics. Product Infrastructure projects own persistence, messaging,
observability, and other runtime adapters.

## Canonical Default

The default Domain contract is interface-first:

```csharp
public interface IDomainEntity<out TId> where TId : notnull
{
    TId Id { get; }
}

public interface IAggregateRoot<out TId> : IDomainEntity<TId>
    where TId : notnull
{
}

public interface IDomainEvent
{
    Guid EventId { get; }
    DateTimeOffset OccurredOn { get; }
}
```

- A normal Aggregate implements `IAggregateRoot<TId>` directly.
- An Entity may implement `IDomainEntity<TId>` directly.
- A Value Object normally uses a C# `record` or `record struct`.
- `DomainEntity<TId>`, `AggregateRoot<TId>`, and `ValueObject` base classes are
  not part of the default profile.
- Shared test base classes remain prohibited.

The repository and integration contracts are semantic ports, not implementation
frameworks:

- `IAggregateRepository<TAggregate, TId>` exposes Aggregate lookup and save
  semantics;
- query ports are read-only and separate from Aggregate repositories;
- physical purge, Outbox, Projection, Import, and similar writers use
  capability-specific ports;
- integration publishing is an Application-owned port when messaging is
  selected;
- EF Core, Dapper, Wolverine, brokers, tracing, and AOP implementations belong
  to target Infrastructure or CrossCutting projects.

Look up target-owned event mapping, serializers, outbox and query writers,
repository aliases and in-memory test adapters before adding any type. The
[generation guide](../../tooling/generation/README.md) locates the
`domain-contracts` and optional `es-aggregate` snippets. Any generated code
belongs to the target and needs local verification.

## Optional `EsAggregateRoot<TId>` Behavior Contract

Rule ID: `AGGREGATE-ES-001` (`conditional` when Event Sourcing is selected).

`EsAggregateRoot<TId>` is the only supplied optional base class. A target may
render the ES snippet, reimplement this contract, or use another implementation
that preserves the behavior.

### Required behavior

1. `Replay(history)` dispatches committed events to `When` in order.
2. Replay increments the committed `Version` once per event.
3. Replay never adds events to the pending-event collection.
4. `Apply(event)` dispatches the event to `When` before recording it as pending.
5. If `When` rejects an event, that event is not recorded as pending.
6. `Apply` does not advance the committed `Version`.
7. `MarkChangesAsCommitted(committedVersion)` accepts only
   `Version + pending-count`.
8. A successful commit advances `Version` and clears pending events exactly
   once.
9. A rejected commit confirmation preserves the committed version and pending
   events for retry or diagnosis.
10. Product state changes occur only in `When`; `When` is deterministic and
    performs no external I/O.

Reconstruction failure MUST expose no command-usable partial Aggregate. The
caller discards an instance after replay/transition failure; the reference-only
snippet does not promise rollback or automatic poisoning. Historical
event/schema compatibility and migration are target-owned. New pending events
are acknowledged only after durable append/commit; an unknown storage result
requires reconciliation, not blind retry or clearing. A generic
`ClearDomainEvents` call is not part of this behavior contract. Equivalent custom
APIs are valid when their semantics are verified. The published ArchPrecept
CT-005 API is a separate optional implementation; see the
[contract cases](../../testing/reconstruction-and-projector-cases.md).

### Construction rule

Do not invoke virtual `When` from the base constructor. In C#, a derived type's
field initializers have not completed while its base constructor executes.
The derived reconstruction constructor calls `Replay(history)` from its own
constructor body:

```csharp
public sealed class Order : EsAggregateRoot<OrderId>
{
    private readonly List<OrderLine> _lines = [];

    public Order(IEnumerable<IDomainEvent> history)
    {
        Replay(history);
    }

    protected override void When(IDomainEvent @event)
    {
        // deterministic type dispatch
    }
}
```

The `domain-contracts` and `es-aggregate` snippets provide the reference mechanics.
See the [generation guide](../../tooling/generation/README.md). Generated code is
target-owned and requires compilation and behavior verification.

## Generated Source Ownership

After generation:

1. generated source belongs to the target;
2. the target records namespace changes and local behavior changes as target
   evidence;
3. a target-selected, actually available maintenance procedure compares the
   recorded framework base, incoming framework source, and target-owned copy;
4. that procedure proposes reconciliation and never overwrites target-owned
   truth solely because the framework copy changed.

## Architectural Equivalence Checks

| Criterion | Deterministic check or review evidence |
| --- | --- |
| Bounded-context grammar | project-structure profile validation plus reviewer confirmation of workload mapping |
| Dependency direction | target-selected analyzer/architecture checks or explicit structural review |
| Port ownership | repository, query, messaging, and purge checklist |
| Aggregate/Repository semantics | `DBA1001`, `DBA1003`, `DBA1009`, and Aggregate review checklist |
| Deletion policy | `DELETE-SOFT-001` selection or explicit target opt-out evidence |
| CQRS/MQ boundary | Use Case/Handler and cross-BC communication checks |
| Technology profile | `technologySelections` schema validation and target override evidence |
| ES mechanical behavior | target-owned behavior tests plus optional target-selected `DBA1009` positive/negative analyzer tests |

No class-name index by itself proves reconstructability.

## Deferred

- a complete BuildingBlocks solution;
- a golden SampleProduct;
- target persistence, broker, observability, or AOP implementations;
- automatic rewriting of target-owned source copies.
