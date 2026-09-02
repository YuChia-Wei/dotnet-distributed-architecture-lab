# .NET Tech Stack Requirements

本文件記錄 `dotnet-mq-arch-lab` 目前由 repository files 證明的技術選型。版本以 `global.json`、產品 `*.csproj`、test projects 與 Docker Compose 為準。

## Current Stack

| Area | Current choice | Evidence-backed version / status |
| --- | --- | --- |
| SDK / Runtime | .NET / C# | SDK `10.0.302` with `latestMajor` roll-forward; product target `net10.0` |
| Web API | ASP.NET Core + OpenAPI + Scalar | ASP.NET Core packages `10.0.7`; Scalar `2.14.3` |
| Messaging | WolverineFx | `5.32.1` |
| Canonical broker | Apache Kafka | Compose image `apache/kafka:4.0.0`; selected for event-driven verification and keyed partition ordering |
| Deferred compatibility broker | RabbitMQ | Wolverine RabbitMQ `5.32.1`; logical listeners exist, Compose service is disabled, and exchange/per-consumer queue/binding/DLQ verification remains pending |
| Persistence | Dapper + Npgsql | Dapper `2.1.72`; Npgsql `10.0.2` |
| Database | PostgreSQL | Compose image `postgres:16.15-alpine` |
| Testing | xUnit + Moq/NSubstitute + Shouldly | xUnit `2.9.3`; test-double package is selected per project; Shouldly `4.3.0` |
| Observability | OpenTelemetry + Grafana stack | OTel SDK `1.15.x`; Collector Contrib `0.159.0`; Grafana `13.2.1`; Tempo `2.10.7`; Loki `3.7.7`; Prometheus `3.14.0` |
| Containers | Docker / Docker Compose | host Dockerfiles plus `docker-compose/docker-compose.yml` |

## Architecture Requirements

- Product code targets .NET 10 and remains Linux-container compatible.
- Bounded contexts follow Domain, Application, Infrastructure, and Presentation dependency boundaries.
- HTTP endpoints enter through explicit application use-case/query ports.
- Cross-context contracts belong under `src/BC-Contracts/`.
- Orders-to-Inventory reservation remains message-mediated through Wolverine request/reply.
- Integration consumers must assume at-least-once delivery unless a stronger guarantee is documented.

## Persistence Requirements

- Write-side repositories use parameterized Dapper/Npgsql access.
- Query repositories currently use Dapper/Npgsql in product source; EF Core is not a product runtime dependency.
- The Orders event-sourcing repository is a context-specific capability and must not be assumed for Product or Inventory.
- Orders and every Inventory event-producing stock command write state plus source-outbox intent in one local transaction. Inventory declares this through capability-specific outbox ports; generic Unit of Work and transaction lifecycle types remain private Infrastructure details, and the relay is a separate adapter.
- Other Inventory stock commands still persist then publish directly; do not generalize the reservation implementation until a separate slice adopts and tests it.
- Credentials, connection strings, database names, and local ports belong in runtime configuration, not in `.dev/project-config.yaml`.

## Messaging Requirements

- Kafka is the canonical checked-in profile. Ordering is scoped to records sharing the same producer-selected partition key; Inventory reservation uses normalized `ProductId`.
- Multiple Kafka consumer groups can independently receive one topic. A broadcast requirement therefore requires an explicit topology comparison before choosing migration or dual deployment.
- RabbitMQ is a compatibility profile and must not be described as broadcast-capable from the current shared queue names. Kafka + RabbitMQ dual broadcast is the target direction, but real connectivity, per-destination outbox state, exchange, per-consumer queue, binding, reply, and DLQ behavior require a separate implementation and environment gate.
- Logical channel ownership and unresolved retry/DLQ details are documented in `.dev/operations/mq-topology.md`.
- Contract meaning and compatibility are owned by the producing bounded context and encoded in its project under `src/BC-Contracts/`; consumers own reaction and delivery handling.

## Testing Requirements

- Product and domain tests use xUnit.
- Test doubles use Moq or NSubstitute according to the owning test project; do not introduce a shared mutable base fixture.
- Assertions use Shouldly where referenced by the test project.
- Product tests and architecture-tool tests are separate validation surfaces because the `tools/` projects are not in `MQArchLab.slnx`.
- `InventoryControl.Tests` owns Inventory application, contract, relay, idempotency, and opt-in PostgreSQL scenarios. External PostgreSQL/broker tests are skipped without explicit opt-in and skipped results are non-passing evidence.

## Version Ownership

- `global.json` owns the selected SDK version.
- Each `*.csproj` owns its package versions.
- `docker-compose/docker-compose.yml` owns checked-in infrastructure image versions.
- README and `.dev/project-config.yaml` are derived views and must be refreshed when those sources change.
