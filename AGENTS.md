# Repository Guidelines

This guide consolidates AI_CLI_PROMPT (EN/zh‑TW) with repo conventions. The system follows Clean Architecture, DDD, and CQRS, using WolverineFx for messaging; PostgreSQL for data; RabbitMQ or Kafka as brokers.

## Project Structure & Module Organization
- Source lives under `src/<Context>` with two groups:
  - `DomainCore`: `<Service>.Applications`, `<Service>.Domains`, `<Service>.Infrastructure` (pluralized layer names).
  - `Presentation`: `<Service>.WebApi`, `<Service>.Consumer` (every executable includes a `Dockerfile`).
- Shared libraries: `src/BuildingBlocks`, `src/BC-Contracts` (message schemas), `src/Shared` (kernel).
- Tooling/data: `docker-compose/`, `sql-script/`, docs in `doc/`. Solution: `MQArchLab.slnx` with folders mirroring directories.

## Build, Test, and Development Commands
- Restore/build: `dotnet restore` && `dotnet build` (run at repo root).
- Run APIs: `dotnet run --project src/Order/Presentation/SaleOrders.WebApi` (Products analogous).
- Run consumers: `dotnet run --project src/Order/Presentation/SaleOrders.Consumer` (Products analogous).
- Select broker: set `QUEUE_SERVICE=Kafka` or `RabbitMQ`; set `ConnectionStrings__KafkaBroker` / `ConnectionStrings__MessageBroker` accordingly.
- Full local stack: `docker-compose -f ./docker-compose/docker-compose.yml up -d`.

## Coding Style & Naming Conventions
- `.editorconfig`: spaces, CRLF, 150 cols; sort `using` with `System` first; namespaces match folders.
- Naming: interfaces `I*`; types/methods/properties PascalCase; instance fields `_camelCase`; prefer file‑scoped namespaces.
- DI per project via `AddApplicationServices` and `AddInfrastructureServices` extension methods.
- API DTOs: input `*Request`, output `*Response`. Scalar is enabled for OpenAPI docs in WebApi.

## Testing Guidelines
- Framework: xUnit. Create `*.Tests` projects near the target (e.g., `tests/SaleProducts.Domains.Tests`). Classes named `<TypeName>Tests`. Run with `dotnet test`.

## Commit & Pull Request Guidelines
- Commits: short, imperative, optional scope (e.g., `orders: enable Kafka auto-provision`); mention generator when relevant (e.g., “by gemini cli”).
- PRs: motivation, linked issues, impacted services/projects, and local evidence (Scalar/Kafka/RabbitMQ screenshots or logs). Use `.github/pull_request_template.md`.

## Security & Configuration Tips
- Use env vars/secrets; never commit credentials. Local UIs: Kafka `http://localhost:19000`, RabbitMQ `http://localhost:15672` (guest/guest, dev only).

