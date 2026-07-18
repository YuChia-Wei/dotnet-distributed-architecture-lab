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

## Optional `EsAggregateRoot<TId>` Behavior Contract

Rule ID: `AGGREGATE-ES-001` (`conditional` when Event Sourcing is selected).

`EsAggregateRoot<TId>` is the only supplied optional base class. A target may
copy the source include, reimplement this contract, or use another implementation
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

The repository-owned source include is under
[`source-includes/domain/`](../../.ai/assets/tech-stacks/dotnet-backend/source-includes/domain/). Its behavior is compiled
and tested by
[`tools/DotnetBackendBuildingBlocks.Tests`](../../tools/DotnetBackendBuildingBlocks.Tests/).
It is not a published package or complete reference product.

## Source-Include Ownership And Upgrade Rule

Until a package distribution decision exists:

1. copying a source include into a target makes the copy target-owned;
2. the target records namespace changes and local behavior changes as target
   evidence;
3. `ai-context-upgrader` compares the recorded framework base, incoming
   framework source, and target copy;
4. the upgrader proposes reconciliation and never overwrites target-owned truth
   solely because the framework copy changed.

## Provenance And Concept Disposition

| Source evidence | Historical shape | Current disposition | Reason |
| --- | --- | --- | --- |
| `ai-coding-exercise` at `f7ed0b9b5b23822ec012c375261df44f6f03a97f` | Java EzDDD `EsAggregateRoot<TId,TEvent>`, `apply/when`, replay constructor | Preserve event-transition and replay concepts; retire Java generic/API shape from active .NET truth | Framework-specific Java types are provenance, not portable .NET contracts |
| `dotnet-mq-arch-lab` | `EsAggregateRoot<TId>` plus `DomainEntity` and `AggregateRoot` bases; explicit commit lifecycle | Preserve single-generic ES shape and commit lifecycle; do not require the other bases | The ES mechanics have executable downstream evidence; the inheritance chain is not required |
| `dotnet-webapi-lab` | State-based Aggregates implement `IAggregateRoot<Guid>` directly | Preserve as evidence for interface-first normal Aggregates | Confirms that useful Aggregate models do not require a common base class |
| Pre-v0.4.0 framework example | Converted `EsAggregateRoot<TId,TEvent>` placeholder embedded in `Plan.cs` | Rewrite to the canonical single-generic contract and keep the portfolio illustrative | Embedded placeholder contradicted `DBA1009` guidance and had no independent test route |
| `DBA1009` | Detects descendants named `EsAggregateRoot` | Keep type-hierarchy recognition and test the canonical single-generic shape | The diagnostic must apply to target reimplementations as well as the supplied source include |

These repositories are evidence sources only. A target must be reconstructable
from this repository's current standards and navigation without access to them.

## Architectural Equivalence Checks

| Criterion | Deterministic check or review evidence |
| --- | --- |
| Bounded-context grammar | project-structure profile validation plus reviewer confirmation of workload mapping |
| Dependency direction | analyzer/structural dependency checks |
| Port ownership | repository, query, messaging, and purge checklist |
| Aggregate/Repository semantics | `DBA1001`, `DBA1003`, `DBA1009`, and Aggregate review checklist |
| Deletion policy | `DELETE-SOFT-001` selection or explicit target opt-out evidence |
| CQRS/MQ boundary | Use Case/Handler and cross-BC communication checks |
| Technology profile | `technologySelections` schema validation and target override evidence |
| ES mechanical behavior | `DotnetBackendBuildingBlocks.Tests` plus `DBA1009` positive/negative tests |

No class-name index by itself proves reconstructability.

## Deferred

- NuGet or `dotnet new` distribution;
- a complete BuildingBlocks solution;
- a golden SampleProduct;
- target persistence, broker, observability, or AOP implementations;
- automatic rewriting of target-owned source copies.
