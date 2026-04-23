# Architecture Playbook

This file distills the repo's non-negotiable architecture constraints for design work.

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

- Use `.dev/project-config.yaml` as the architecture mode source of truth when the task depends on profile or persistence mode.
- Cross-BC communication must use RabbitMQ or Kafka only.
- Do not route BC collaboration through direct web API calls.
- Use generic repository abstractions only; domain behavior belongs in aggregates or application services.
- Use `IServiceCollection` registration, not scanning.
- Write side: Dapper + Npgsql.
- Read/projection side: EF Core or Dapper.
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
