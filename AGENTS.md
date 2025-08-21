# Repository Guidelines

Single source of truth for contributors and AI. Architecture: Clean Architecture + DDD + CQRS. Messaging via WolverineFx; PostgreSQL for data; RabbitMQ or Kafka for brokers.

## Project Structure & Rules
- Source under `src/<Context>` only. Two groups:
  - `DomainCore`: `<Service>.Applications`, `<Service>.Domains`, `<Service>.Infrastructure` (pluralized layer names).
  - `Presentation`: `<Service>.WebApi`, `<Service>.Consumer` (every executable must include a `Dockerfile`).
- Shared libs: `src/BuildingBlocks`, `src/BC-Contracts` (message schemas), `src/Shared` (kernel).
- Tooling/data: `docker-compose/`, `sql-script/`, docs in `doc/`. Solution: `MQArchLab.slnx` with solution folders mirroring directories.
- API DTO naming: input `*Request`, output `*Response`. Public API summaries should be present (zh‑TW preferred).

## Development Workflow (AI + Humans)
1) Confirm scope: service name (e.g., Invoices), context folder (e.g., `Invoice`), layers to create.
2) Create projects in correct paths (examples):
   - `dotnet new webapi -n Invoices.WebApi -o src/Invoice/Presentation/Invoices.WebApi`
   - `dotnet new classlib -n Invoices.Applications -o src/Invoice/DomainCore/Invoices.Applications`
3) Add to solution with matching solution folders:
   - `dotnet sln add src/Invoice/Presentation/Invoices.WebApi/Invoices.WebApi.csproj --solution-folder "Invoice/Presentation"`
4) Add DI extension methods inside each project (e.g., `AddApplicationServices`, `AddInfrastructureServices`).
5) Ensure Dockerfile for every executable (API/Consumer) using multi‑stage build. Compose entries go in `docker-compose/docker-compose.yml` if needed.

## Build, Run, and Brokers
- Build: `dotnet restore` && `dotnet build` (repo root).
- Run APIs/consumers:
  - Orders API: `dotnet run --project src/Order/Presentation/SaleOrders.WebApi`
  - Orders Consumer: `dotnet run --project src/Order/Presentation/SaleOrders.Consumer` (Products analogous)
- Broker selection via env vars: `QUEUE_SERVICE=Kafka|RabbitMQ` plus `ConnectionStrings__KafkaBroker` or `ConnectionStrings__MessageBroker`.
- Full local stack: `docker-compose -f ./docker-compose/docker-compose.yml up -d`.

## Coding Style
- `.editorconfig` enforced: spaces, CRLF, 150 cols; `System` usings first; namespaces match folders; file‑scoped namespaces preferred; top‑level statements allowed.
- Naming: interfaces `I*`; types/methods/properties PascalCase; instance fields `_camelCase`.

## Testing
- xUnit by default. Tests live in `tests/*/*.Tests.csproj` (e.g., `tests/SaleProducts.Domains.Tests`). Classes named `<TypeName>Tests`. Run with `dotnet test`.

## Commit & PRs
- Commits: short, imperative, optional scope (e.g., `orders: enable Kafka auto-provision`). Note generator when relevant (e.g., “by gemini cli”).
- PRs: describe motivation, linked issues, impacted projects/services, and evidence (Scalar/Kafka/RabbitMQ screenshots/logs). Use `.github/pull_request_template.md`.

## Security & Config
- Use env vars/user-secrets; never commit credentials. Local UIs: Kafka `http://localhost:19000`, RabbitMQ `http://localhost:15672` (guest/guest; dev only).

## PRD Mode (for larger changes)
When scope is broad or token budget matters, include this concise PRD in your first reply:
- Summary: one paragraph of the problem and outcome.
- Goals: 3–6 bullets of what will be delivered.
- Non‑Goals: what is explicitly out of scope.
- Constraints: tech, style, directories, naming, DI, Dockerfile/compose.
- Acceptance Criteria: verifiable checks (builds, runs, endpoints OK, tests pass).
- Plan: 4–8 short steps (create/modify files, commands to run).
