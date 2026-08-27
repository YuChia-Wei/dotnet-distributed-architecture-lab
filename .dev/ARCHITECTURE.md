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

Shared boundaries:

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
- Orders atomically commits domain events, read model state, and its source outbox. Inventory `ReserveInventory` uses an explicit application transaction port so the reservation outcome and `InventoryIntegrationOutbox` row commit or roll back together; other Inventory stock commands have not yet adopted this source-outbox pattern.
- Source-outbox relays are Infrastructure adapters: they do not decide event meaning. They publish the producer-created contract with stable delivery metadata and bounded retry/park behavior.
- Product source projects do not currently reference EF Core; the retired target validation tooling is no longer part of the active repository.

## Messaging And Integration

- WolverineFx is the messaging abstraction used by APIs and consumers.
- Kafka is the canonical broker and event-driven verification path. Inventory reservation events use normalized `ProductId` as their Kafka partition key so events for one product can preserve partition order; no cross-partition global ordering is promised.
- Kafka can deliver one topic to multiple independent consumer groups. A future broadcast requirement therefore triggers a topology comparison, not an automatic RabbitMQ migration.
- RabbitMQ packages and logical request/reply routing remain as a deferred compatibility profile. Its Compose service is commented out, current shared queue names describe competing-consumer behavior rather than fanout, and physical exchange/per-consumer queue/binding/DLQ behavior requires a separate owner decision and runtime proof.
- The producing bounded context owns integration-event meaning, schema, and compatibility. Consumers own only their reactions, projections, idempotency, retry, and dead-letter handling.
- Known logical channels include `orders.integration.events`, `products.integration.events`, `inventory.integration.events`, `inventory.requests`, and `orders.outbound.replies`.
- Orders reserves inventory through `ReserveInventoryRequestContract` / `ReserveInventoryResponseContract` request/reply over Wolverine, not through direct domain references.

See `operations/context-map.md`, `operations/event-catalog.md`, and `operations/mq-topology.md` for operational detail and documented uncertainties.

## Runtime And Deployment

The repository defines six product hosts:

- three ASP.NET Core Web APIs;
- three .NET Generic Host consumers.

`docker-compose/docker-compose.yml` also defines PostgreSQL databases per context, Kafka/Kafdrop, OpenTelemetry Collector, Prometheus, Tempo, Loki, and Grafana. Dockerfiles live in each Presentation host project.

## Tests And Validation Boundary

- `MQArchLab.slnx` includes five xUnit test projects for Products, Orders, and Inventory.
- `InventoryControl.Tests` owns Inventory command/reservation tests. Its real PostgreSQL checks are explicitly opt-in and skipped during ordinary test runs.
- The target-owned analyzer and runtime-validation projects were retired by the owner-approved v0.9 AI-context upgrade and are absent from the repository and solution.
- v0.13 removed the former bundled mechanical-validation provider. The remaining `.ai/assets/tech-stacks/dotnet-backend/tooling/on-demand-mechanical-validation/` assets are reference-only recipes; they are not selected, activated, or wired into the target solution or build.

## Truth Ownership

- Current structure and versions: `MQArchLab.slnx`, `global.json`, `*.csproj`.
- Runtime topology: `docker-compose/`, host `Program.cs`, and appsettings files.
- Business behavior: `src/`, `tests/`, requirements, and validated specs.
- Project inventory: `.dev/project-config.yaml`, regenerated by `repo-structure-sync`.
- Reusable AI collaboration rules: `.ai/assets/`; these do not own product facts.
