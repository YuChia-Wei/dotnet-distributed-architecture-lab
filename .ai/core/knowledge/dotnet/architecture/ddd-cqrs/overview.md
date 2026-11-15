# Selected .NET DDD/CQRS architecture

Use this profile where the target adopts Domain-Driven Design, Clean
Architecture, CQRS and ports/adapters. Confirm the actual [technology
selection](../../core/technology-selection.md) and accepted [project
structure](project-structure.md) before applying physical layout.

## Responsibilities

| Boundary | Owns |
| --- | --- |
| Domain | Aggregates, entities, value objects, domain services, events and invariants, independent of transport, ORM and broker APIs |
| Application | Command, query and reaction entry points, use case orchestration and application-facing ports |
| Infrastructure | Selected persistence, messaging, serialization and external adapters |
| Presentation | HTTP or message delivery, transport DTO binding and invocation of the Application port |

A controller, message handler or scheduled trigger is an inbound adapter.
Repository, event publication, time, identity and external-system dependencies
are outbound ports when the operation needs them. Adapters translate between
protocols and ports while Domain and Application retain their own decisions.
See [Use Case standards](usecase-standards.md) for ordinary API calls and actual
dispatch entries.

## Design checks

- Separate bounded contexts when business language, ownership, lifecycle or
  scaling needs diverge. Share explicitly owned contracts across them.
- Keep a consistency invariant within one Aggregate where possible. Use eventual
  propagation for other Aggregates by default and apply the [same-context
  exception](usecase-standards.md#7-strong-consistency-must-be-explicit) only for
  a documented non-compensable all-or-nothing business requirement.
- Separate commands that own behavior from queries that return read models.
  CQRS can work with conventional state persistence. [Event
  Sourcing](building-blocks-reconstruction.md) applies only when selected.
- Keep write storage at the aggregate-root boundary and read models behind
  read-only ports. [Projector](../../integration/persistence/projection-standards.md),
  [purge](../../integration/persistence/archive-standards.md) and
  [outbox](../../integration/messaging/transactional-messaging-standards.md)
  capabilities have explicit owners. Choose a provider by domain and check
  transaction, concurrency, replay and delivery needs.
- Base cache, projection and batching decisions on a measured workload and
  required freshness. The target's design owns the tradeoff.

## Retained cross-context restrictions

Where the original .NET relationship profile is adopted, cross-BC interaction
uses MQ. The retained architecture playbook specifically permits RabbitMQ or
Kafka and excludes direct web API calls. The applicability difference remains
unresolved and neither statement changes a target's adopted scope. Compare the
two policies and their limits in [policy
rationale](../../references/policy-rationale.md#cross-bc-interaction-retained-restriction-and-scope-gap).

## Evidence for a design

Identify the business capability, data and event owners, port/adapter placement
and governing references. Check project files, dependencies, deployment
configuration and accepted architecture decisions. Use a summary only as a
pointer to that evidence. Select provider registration explicitly at the
[composition root](../../core/host-configuration.md).
