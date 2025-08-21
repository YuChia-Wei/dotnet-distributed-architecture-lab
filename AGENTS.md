# Repository Guidelines

## Project Structure & Module Organization
- src: domain and apps by bounded context.
  - `src/Order` and `src/Product`: `DomainCore` (Applications, Domains, Infrastructure) and `Presentation` (`*.WebApi`, `*.Consumer`).
  - `src/BuildingBlocks`: reusable domain/integration abstractions.
  - `src/BC-Contracts`: cross-BC message schemas (e.g., `Lab.MessageSchemas.Orders`).
  - `src/Shared`: shared kernel.
- docker-compose: `docker-compose/docker-compose.yml` for local stack.
- sql-script: init scripts for Postgres.
- doc: design notes and comparisons.

## Build, Test, and Development Commands
- Restore/build all: `dotnet restore` then `dotnet build` (run at repo root).
- Run Orders API: `dotnet run --project src/Order/Presentation/SaleOrders.WebApi`
- Run Products API: `dotnet run --project src/Product/Presentation/SaleProducts.WebApi`
- Run consumers: `dotnet run --project src/Order/Presentation/SaleOrders.Consumer` and `src/Product/Presentation/SaleProducts.Consumer`
- With broker selection: set `QUEUE_SERVICE=Kafka` or `RabbitMQ` (PowerShell: `$env:QUEUE_SERVICE="Kafka"`).
- Full stack via Docker: `docker-compose -f ./docker-compose/docker-compose.yml up -d`

## Coding Style & Naming Conventions
- Indentation: spaces; line endings: CRLF; max line length 150 (`.editorconfig`).
- Namespaces match folders; prefer `using System` first, grouped.
- Interfaces: `I*`; types/methods/properties: PascalCase; instance fields: `_camelCase`.
- Enable nullable/implicit usings (.csproj). Use `this.` qualification for members.

## Testing Guidelines
- No test projects yet. If adding tests, prefer xUnit.
- Naming: create `*.Tests` projects alongside the target (`src/Order/...`), classes as `<TypeName>Tests`.
- Run tests: `dotnet test` at repo root or project folder.

## Commit & Pull Request Guidelines
- Commits: short, imperative, optionally scoped (e.g., `orders: enable Kafka auto-provision`).
- Reference related tools when relevant (e.g., “by gemini cli”).
- PRs: describe motivation and changes, link issues, note affected services, and include local run proof (e.g., API/consumer output, screenshots of Scalar or Kafka UI).

## Security & Configuration Tips
- Configuration via env vars: `QUEUE_SERVICE`, `ConnectionStrings__MessageBroker`, `ConnectionStrings__KafkaBroker`, and DB connection strings (see compose file).
- Do not commit secrets. For local dev, prefer environment variables or user-secrets.
- Brokers: Kafka UI at `http://localhost:19000`; RabbitMQ at `http://localhost:15672` (guest/guest, dev only).

