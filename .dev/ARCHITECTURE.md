# Architecture

This document describes the current architecture of `dotnet-mq-arch-lab` as supported by source and deployment evidence. Reusable .NET backend guidance lives under `.ai/assets/tech-stacks/dotnet-backend/`; framework examples are not product facts.

## System Overview

The repository is a distributed commerce lab composed of Products, Orders, and Inventory bounded contexts. It uses:

- Domain-Driven Design
- Clean Architecture
- CQRS-oriented application boundaries
- ports and adapters / Hexagonal view
- message-oriented bounded-context integration
- context-specific aggregate persistence, including event sourcing for Orders
- Wolverine durable Outbox/Inbox messaging at configured runtime adapters

## Bounded Contexts

| Context | Source root | Domain namespace | Primary aggregate | Hosts |
| --- | --- | --- | --- | --- |
| Products | `src/Product/` | `SaleProducts.Domains` | `Product` | `SaleProducts.WebApi`, `SaleProducts.Consumer` |
| Orders | `src/Order/` | `SaleOrders.Domains` | `Order` | `SaleOrders.WebApi`, `SaleOrders.Consumer` |
| Inventory | `src/Inventory/` | `InventoryControl.Domains` | `InventoryItem` | `InventoryControl.WebApi`, `InventoryControl.Consumer` |

Shared boundaries：

- `src/BC-Contracts/` owns cross-context request/reply contracts and integration events.
- `src/BuildingBlocks/` owns business-neutral domain, application, and integration abstractions.
- `src/Shared/Lab.SharedKernel/` is currently an empty placeholder project for deliberately shared domain concepts; it owns no implemented concepts yet.

## Context Project Shape

Each bounded context currently follows the same primary physical shape:

```text
<Context>/
  DomainCore/
    *.Domains/
    *.Applications/
    *.Infrastructure/
  Presentation/
    *.WebApi/
    *.Consumer/
```

- Domain project owns aggregates, entities, value objects, domain events, and invariants.
- Application project owns use-case ports, orchestration, query services, gateways, and repository ports.
- Infrastructure project adapts persistence, messaging, and external collaboration.
- Web API and Consumer projects are inbound adapters and composition roots.

## Application Boundaries

- HTTP controllers depend on explicit `I<Operation>UseCase` ports and invoke `ExecuteAsync`.
- Query use cases/services expose read behavior without moving domain mutation into controllers.
- Message handlers belong at message-oriented entry points and delegate business work to application use cases.
- Application code should depend on project-owned ports; Wolverine-specific behavior belongs in adapters/composition unless an existing compatibility boundary requires otherwise.

Current use cases include product create/update/delete/query, order place/ship/deliver/cancel/query, and inventory initialize/increase/decrease/restock/query behavior.

## Persistence

- Product and Inventory persistence use Dapper + Npgsql repositories with PostgreSQL.
- Order includes both a Dapper domain repository and `OrderEventSourcingRepository`; event sourcing is an explicit Orders capability rather than a universal default.
- Integration publishing is coordinated through repository/infrastructure code and Wolverine durable messaging facilities.
- Product source projects do not currently reference EF Core; EF Core packages are present only in validator test tooling.

## Messaging And Integration

- WolverineFx is the messaging abstraction used by APIs and consumers.
- Kafka is enabled by the checked-in Docker Compose topology.
- RabbitMQ packages and partial conditional runtime configuration are retained, while its Compose service is commented out and the Inventory request/reply listener path is not currently complete.
- Known logical channels include `orders.integration.events`, `products.integration.events`, `inventory.integration.events`, `inventory.requests`, and `orders.outbound.replies`.
- Orders reserves inventory through `ReserveInventoryRequestContract` / `ReserveInventoryResponseContract` request/reply over Wolverine, not through direct domain references.

See `operations/context-map.md`, `operations/event-catalog.md`, and `operations/mq-topology.md` for operational detail and documented uncertainties.

## Runtime And Deployment

The repository defines six product hosts:

- three ASP.NET Core Web APIs;
- three .NET Generic Host consumers.

`docker-compose/docker-compose.yml` also defines PostgreSQL databases per context, Kafka/Kafdrop, OpenTelemetry Collector, Prometheus, Tempo, Loki, and Grafana. Dockerfiles live in each Presentation host project.

## Tests And Architecture Tooling

- `MQArchLab.slnx` includes four xUnit test projects for Products and Orders.
- Inventory currently has no test project in the solution.
- `tools/DotnetBackendAnalyzers*` provides Roslyn architecture analyzers and tests.
- `tools/DotnetBackendValidation*` provides runtime validation helpers and tests.
- Tool projects are not currently included in `MQArchLab.slnx`.

## Truth Ownership

- Current structure and versions: `MQArchLab.slnx`, `global.json`, `*.csproj`.
- Runtime topology: `docker-compose/`, host `Program.cs`, and appsettings files.
- Business behavior: `src/`, `tests/`, requirements, and validated specs.
- Project inventory: `.dev/project-config.yaml`, regenerated by `repo-structure-sync`.
- Reusable AI collaboration rules: `.ai/assets/`; these do not own product facts.
