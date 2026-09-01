# .NET Distributed Messaging Architecture Lab

[繁體中文](README.md)

This document is the English translation of the canonical Traditional Chinese repository `README.md`.

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

- .NET SDK `10.0.302` (`global.json` permits `latestMajor` roll-forward), with `net10.0` as the primary target framework
- ASP.NET Core Web API and Scalar OpenAPI UI
- WolverineFx `5.32.1`
- Kafka (the canonical broker; enabled in Docker Compose, with producer-selected partition keys used to verify per-business-entity ordering)
- RabbitMQ (a deferred compatibility profile; its Compose service is commented out, current shared queues are not broadcast topology, and migration or dual deployment requires a separate evaluation)
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

The current Compose topology starts three API/Consumer pairs, an authentication-free YARP Gateway, three PostgreSQL databases, Kafka/Kafdrop, and the OpenTelemetry/Grafana observability stack.

Default API entry points:

- YARP Gateway (authentication-free): `http://localhost:8888` (`/api/orders`, `/api/products`, and `/api/inventory`)
- Orders API: `http://localhost:8080`
- Products API: `http://localhost:8090`
- Inventory API: `http://localhost:8100`

### Verify Wolverine Consumer Exception Handling

Compose explicitly enables a lab-only exception-policy probe. When the Product API is started with other configuration, this capability is disabled by default and returns HTTP 404. A probe does not modify product, inventory, or order data.

Trigger the timeout policy through the authentication-free YARP Gateway:

```powershell
$probe = Invoke-RestMethod -Method Post `
  -Uri http://localhost:8888/api/products/diagnostics/consumer-exception-policy/timeout
$probe
```

Or trigger the fallback policy for an unclassified exception:

```powershell
$probe = Invoke-RestMethod -Method Post `
  -Uri http://localhost:8888/api/products/diagnostics/consumer-exception-policy/unhandled
$probe
```

Both endpoints return HTTP 202 and a `probeId` that correlates the complete processing path. An unsupported failure kind returns HTTP 400.

Use the returned `probeId` to inspect Orders Consumer handler executions:

```powershell
$handlerPattern = "Consumer exception policy probe $($probe.probeId) is throwing"
docker logs orders-consumer 2>&1 | Select-String -SimpleMatch $handlerPattern
```

Expect `timeout` to execute 4 times in total (the initial attempt plus 3 scheduled retries), and `unhandled` to execute 2 times (the initial attempt plus 1 retry). After all attempts are exhausted, the message reaches the Kafka native dead-letter topic `wolverine-dead-letter-queue`.

Find the exception type, `attempts` header, and payload for this probe in the DLQ:

```powershell
docker exec kafka /opt/kafka/bin/kafka-console-consumer.sh `
  --bootstrap-server localhost:9092 `
  --topic wolverine-dead-letter-queue `
  --from-beginning `
  --timeout-ms 10000 `
  --property print.headers=true 2>&1 |
  Select-String $probe.probeId
```

The terminal record for `timeout` should contain `System.TimeoutException` and `attempts:4`; `unhandled` should contain `System.InvalidOperationException` and `attempts:2`. The topic retains earlier lab messages, so filter with the `probeId` returned by the current request.

Run the solution tests:

```powershell
dotnet test MQArchLab.slnx
```

This repository currently has no active target-owned analyzer or runtime-validator projects. They were retired during the governed v0.9 AI-context upgrade, and v0.13 also removed the former bundled mechanical-validation provider. Only reference-only recipes remain under `.ai/assets/tech-stacks/dotnet-backend/tooling/on-demand-mechanical-validation/`; they are not selected, included in `MQArchLab.slnx`, wired into the build, or activated.

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
