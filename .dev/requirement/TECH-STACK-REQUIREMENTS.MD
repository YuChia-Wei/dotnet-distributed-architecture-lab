# .NET Tech Stack Requirements

本文件記錄 `dotnet-mq-arch-lab` 目前由 repository files 證明的技術選型。版本以 `global.json`、產品 `*.csproj`、test projects 與 Docker Compose 為準。

## Current Stack

| Area | Current choice | Evidence-backed version / status |
| --- | --- | --- |
| SDK / Runtime | .NET / C# | SDK `10.0.0`; product target `net10.0` |
| Web API | ASP.NET Core + OpenAPI + Scalar | ASP.NET Core packages `10.0.7`; Scalar `2.14.3` |
| Messaging | WolverineFx | `5.32.1` |
| Active local broker | Apache Kafka | Compose image `apache/kafka:4.0.0` |
| Partial broker profile | RabbitMQ | Wolverine RabbitMQ `5.32.1`; Compose service disabled and Inventory request listener incomplete |
| Persistence | Dapper + Npgsql | Dapper `2.1.72`; Npgsql `10.0.2` |
| Database | PostgreSQL | Compose image `postgres:16-alpine` |
| Testing | xUnit + Moq + Shouldly | xUnit `2.9.3`; Moq `4.20.72`; Shouldly `4.3.0` |
| Observability | OpenTelemetry + Grafana stack | OTel `1.15.x`; Grafana `11.1.0`; Tempo `2.3.0`; Loki `3.5.3` |
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
- Persistence and integration publication must preserve the repository's documented transaction/outbox semantics.
- Credentials, connection strings, database names, and local ports belong in runtime configuration, not in `.dev/project-config.yaml`.

## Messaging Requirements

- Kafka is the checked-in active local profile.
- RabbitMQ must not be described as a complete profile until the Inventory request listener and request/reply path are configured and verified.
- Logical channel ownership and unresolved retry/DLQ details are documented in `.dev/operations/mq-topology.md`.
- Contract compatibility is owned by projects under `src/BC-Contracts/`.

## Testing Requirements

- Product and domain tests use xUnit.
- Test doubles use Moq in current solution test projects; do not infer NSubstitute from reusable framework examples.
- Assertions use Shouldly where referenced by the test project.
- Product tests and architecture-tool tests are separate validation surfaces because the `tools/` projects are not in `MQArchLab.slnx`.
- Inventory has no checked-in test project and should be treated as a visible coverage gap, not silently inferred as covered.

## Version Ownership

- `global.json` owns the selected SDK version.
- Each `*.csproj` owns its package versions.
- `docker-compose/docker-compose.yml` owns checked-in infrastructure image versions.
- README and `.dev/project-config.yaml` are derived views and must be refreshed when those sources change.
