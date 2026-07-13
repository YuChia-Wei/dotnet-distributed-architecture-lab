# Architecture

This document provides the entry point for reusable .NET backend architecture context. See [TECH-STACK-REQUIREMENTS.MD](./requirement/TECH-STACK-REQUIREMENTS.MD) for detailed technology choices and the conditional [project-structure profile](./standards/project-structure.md) for one target layout that must be confirmed by repository evidence or explicit adoption.

## Architecture Overview

### Core Architecture
- **Style**: Clean Architecture + DDD + CQRS
- **Patterns**: Outbox / InMemory / Event Sourcing (configured per aggregate)
- **Use Case Categories**: Command / Query / Reactor

### Code Organization (Conceptual Layers)
- **Domain**: Aggregates, Entities, Value Objects, Domain Events
- **Application**: Use Cases (Command/Query/Reactor ports)
- **Infrastructure**: Persistence adapters / ORM or direct SQL / Messaging / Integration
- **Adapter**: REST API Controllers, DTOs

For a conditional physical layout and naming example, see [project-structure.md](./standards/project-structure.md). Do not infer that profile as this framework repository's current structure or as a universal target requirement.

### Persistence Port Model

- `IAggregateRepository<TAggregate, TId>`: The canonical Aggregate Root persistence port.
- `IDomainRepository<TAggregate, TId>`: A compatibility port for existing products that inherits from `IAggregateRepository`.
- `IQueryRepository`: A pure query port marker.
- Writes such as physical purge, Outbox, Projection, and Import use capability-specific ports.
- A child Entity must not own a Repository that can be injected independently by the Application layer.
- The target repository determines the database, ORM, event store, and packages.
- Batch Aggregate persistence is a target-specific opt-in capability, not part of the portable default contract.

Terminology and responsibility boundaries:

- See [USECASE-COMMAND-HANDLER-RELATIONSHIP.MD](./standards/USECASE-COMMAND-HANDLER-RELATIONSHIP.MD) for the relationships among `Use Case`, `Command`, `Query`, and `Handler`.

### Application Inbound Port Model

- `I<Operation>UseCase` is an Application inbound port.
- `<Operation>UseCase` implements application orchestration through `ExecuteAsync`.
- By default, an HTTP Controller depends directly on a Use Case interface.
- Only explicitly approved pure-query endpoints may connect directly to a read-only Query Repository/Service as an exception.
- A Command/message Handler exists only at an actual dispatch entry and calls one Use Case after mapping; a Handler must not become the Use Case implementation.
- A Use Case depends on a project-owned outbound event publisher port and does not depend directly on Wolverine `IMessageBus`.
- Wolverine/MediatR/MQ-specific Handlers belong at the inbound adapter/composition boundary; only package-neutral convention Handlers may remain in the Application layer.

### Target Repository Configuration

This framework repository does not retain a product-specific `.dev/project-config.yaml`.

When the framework is introduced into a target repository, first use `repo-structure-sync` to scan repository evidence, then generate `.dev/project-config.yaml` from `.ai/assets/skills/repo-structure-sync/templates/project-config.template.yaml`. Unconfirmed architecture, database, messaging, frontend, or deployment facts must remain blank.

The EF Core, Dapper, Npgsql, WolverineFx, RabbitMQ, and Kafka documents in this framework are conditional/reference guidance and must not automatically become mandatory truth for a target repository.
