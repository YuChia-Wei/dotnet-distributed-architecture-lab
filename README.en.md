# .NET Distributed Messaging Architecture Lab

[繁體中文](README.md)

This document is the English translation of the canonical Traditional Chinese repository README, [`README.md`](README.md).

`dotnet-mq-arch-lab` is a distributed commerce sample project built with .NET 10. It implements and validates DDD, Clean Architecture, CQRS, event-driven integration, Outbox, Event Sourcing, and message-queue-based collaboration between bounded contexts.

The repository also maintains a reusable AI collaboration context. Product truth is owned by `src/`, `tests/`, `docker-compose/`, and validated project documentation under `.dev/`, while portable AI rules are owned by `.ai/assets/`.

## Bounded Contexts

| Context | Responsibility | Runtime hosts |
| --- | --- | --- |
| Products | Create, query, update, and delete products | `SaleProducts.WebApi`, `SaleProducts.Consumer` |
| Orders | Create orders and manage the shipped/delivered/cancelled lifecycle | `SaleOrders.WebApi`, `SaleOrders.Consumer` |
| Inventory | Initialize, increase, decrease, and replenish product inventory | `InventoryControl.WebApi`, `InventoryControl.Consumer` |

Cross-context contracts are located under `src/BC-Contracts/`. The inventory reservation flow between Orders and Inventory collaborates through Wolverine request/reply and MQ channels; integration events are published through the topic/queue owned by each context.

## Technology Stack

- .NET SDK `10.0.0`, with `net10.0` as the primary target framework
- ASP.NET Core Web API and Scalar OpenAPI UI
- WolverineFx `5.32.1`
- Kafka (the broker currently enabled in Docker Compose)
- RabbitMQ (packages and partial conditional configuration are retained; the Compose service is commented out and the Inventory request listener is not fully configured)
- PostgreSQL 16, Dapper `2.1.72`, and Npgsql `10.0.2`
- xUnit `2.9.3`, Moq, and Shouldly
- OpenTelemetry, Prometheus, Tempo, Loki, and Grafana

For exact versions and evidence paths, see [.dev/project-config.yaml](.dev/project-config.yaml) and [.dev/requirement/TECH-STACK-REQUIREMENTS.MD](.dev/requirement/TECH-STACK-REQUIREMENTS.MD).

## Project Structure

```text
src/
  BC-Contracts/       Cross-bounded-context contracts
  BuildingBlocks/     Shared abstractions without business semantics
  Shared/             Shared Kernel placeholder with no domain concepts yet
  Product/            Products bounded context
  Order/              Orders bounded context
  Inventory/          Inventory bounded context
tests/                 Product and domain tests
tools/                 Roslyn analyzers and runtime validators
docker-compose/        Local services and observability topology
sql-script/            PostgreSQL initialization scripts
.dev/                  Project knowledge, requirements, specs, operations, and workflows
.ai/                   Canonical reusable AI context
.agents/, .claude/     Runtime-specific skill wrappers
```

The solution entry point is `MQArchLab.slnx`. Product projects are organized into `DomainCore` and `Presentation` layers; each bounded context owns Application, Domain, Infrastructure, Web API, and Consumer projects.

## Start the Local Environment

Prerequisites:

- .NET 10 SDK
- Docker and Docker Compose

Start the complete environment:

```powershell
docker compose -f ./docker-compose/docker-compose.yml up -d --build
```

The current Compose topology starts three API/Consumer pairs, three PostgreSQL databases, Kafka/Kafdrop, and the OpenTelemetry/Grafana observability stack.

Default API entry points:

- Orders API: `http://localhost:8080`
- Products API: `http://localhost:8090`
- Inventory API: `http://localhost:8100`

Run the solution tests:

```powershell
dotnet test MQArchLab.slnx
```

Analyzer and validator tests are located under `tools/`. They are not currently included in `MQArchLab.slnx` and must be run through their individual test projects.

## Project Knowledge Entry Points

- [.dev/ARCHITECTURE.md](.dev/ARCHITECTURE.md): current product architecture and dependency boundaries
- [.dev/requirement/distributed-commerce-bounded-context-overview.md](.dev/requirement/distributed-commerce-bounded-context-overview.md): bounded-context requirement baseline
- [.dev/specs/INDEX.MD](.dev/specs/INDEX.MD): domain and test specs
- [.dev/operations/context-map.md](.dev/operations/context-map.md): context relationships
- [.dev/operations/event-catalog.md](.dev/operations/event-catalog.md): events and request/reply contracts
- [.dev/operations/mq-topology.md](.dev/operations/mq-topology.md): Kafka/RabbitMQ topology

## AI Collaboration Entry Points

- `AGENTS.md`: canonical agent collaboration guide
- `.ai/INDEX.MD`: canonical AI asset index
- `.ai/assets/skills/README.MD`: canonical skill registry
- `.agents/skills/README.md` and `.claude/skills/README.md`: runtime wrappers
- `.dev/guides/ai-collaboration-guides/README.MD`: human-facing usage guide

If an AI context update causes project truth to be overwritten by source-framework content, use `repo-structure-sync` to rebuild it from repository evidence. Do not directly reuse the source repository's product names, credentials, ports, domains, or workflow records.
