# Architecture Playbook

This file distills the repo's non-negotiable architecture constraints for design work.
Detailed Aggregate transaction and exceptional Unit of Work criteria are owned by
[Aggregate Standards](../../../../../.dev/standards/coding-standards/aggregate-standards.md)
and [Use Case Standards](../../../../../.dev/standards/coding-standards/usecase-standards.md#7-strong-consistency-must-be-explicit).

## Primary Style

- DDD + Clean Architecture + CQRS is the base architecture.
- Use Hexagonal Architecture as the port-and-adapter interpretation of those layers.
- Use MQ-first integration between bounded contexts.

## Layer Intent

### Domain
- Own aggregates, entities, value objects, domain services, domain events, invariants.
- Stay free from transport, ORM, and broker concerns.

### Application
- Own commands, queries, reactors, use case orchestration, and port definitions.
- Translate between domain behavior and external dependencies through ports.

### Infrastructure
- Own persistence adapters, MQ adapters, serializers, outbox plumbing, and external gateway implementations.

### Presentation
- Own HTTP controllers, consumer hosts, request/response DTO binding, and endpoint-specific concerns.

## Repo Constraints

- Use repository code and project evidence as architecture truth. A generated `.dev/project-config.yaml` may be used as a secondary summary when present.
- Cross-BC communication must use RabbitMQ or Kafka only.
- Do not route BC collaboration through direct web API calls.
- Use `IAggregateRepository<TAggregate, TId>` for aggregate-root writes; retain
  `IDomainRepository<TAggregate, TId>` only as the documented compatibility alias.
- Use read-only `IQueryRepository` ports for query models. Add a query service only
  when composition, policy, or calculation requires one.
- Do not expose a public generic writable CRUD repository.
- Keep the portable aggregate repository single-aggregate. A target repository may
  define a batch port only after measured need and explicit batch semantics.
- One command changes one Aggregate by default. Use events and eventual consistency
  for effects involving other Aggregates.
- Use an explicit unit-of-work port for multiple Aggregates only when a documented,
  named all-or-nothing invariant exists inside one bounded context, an intermediate
  eventual state is unacceptable and non-compensable, and the Aggregate boundaries
  have been rechecked. Record the involved Aggregates and why eventual consistency
  or compensation is insufficient.
- Never choose a multi-Aggregate transaction because of I/O reduction, shared
  storage, ORM/framework capability, implementation convenience, or a general
  future need. Do not make unit of work a default dependency, and never span bounded
  contexts with one transaction.
- Use `IServiceCollection` registration, not scanning.
- Persistence and query technologies are target-repository decisions. Apply
  technology-specific rules only when the selected adapter uses that technology.
- Testing: xUnit + NSubstitute, no `BaseTestClass`.

## HEX Interpretation

Apply these mappings consistently:

- Inbound port: command/query/reaction entry point in application layer
- Outbound port: persistence, broker, time, identity, or third-party dependency abstraction
- Inbound adapter: controller, MQ consumer, scheduled trigger
- Outbound adapter: repository implementation, outbox publisher, API client, broker publisher

Do not let adapters define business decisions.

## Design Heuristics

### Bounded Context
- Split when language, lifecycle, ownership, or scaling differ.
- Share contracts, not internals.

### Aggregate
- Keep transactional consistency inside one aggregate.
- Use events for side effects and cross-aggregate propagation.
- Treat same-bounded-context multi-Aggregate consistency as an exception governed
  by [Use Case Standards](../../../../../.dev/standards/coding-standards/usecase-standards.md#7-strong-consistency-must-be-explicit),
  not as a reusable default architecture pattern.

### Command/Query
- Command side owns behavior and invariants.
- Query side owns read models, archives, projections, and client-facing shape.

### Reactor
- Consume event data and coordinate eventual consistency.
- Avoid loading unrelated aggregates unless the design explicitly requires a query-side lookup.

## Documentation Expectations

For any architecture proposal, state:

- business capability or use case
- layer placement
- port and adapter boundaries
- data ownership and integration event ownership
- canonical rule/doc references that justify the design
