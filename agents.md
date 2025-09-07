# Repository Guidelines

## Scope & Precedence
- Applies to the entire repository for both AI agents and humans.
- Deeper AGENTS files override higher-level ones.
- Rule order: User/approval > deeper AGENTS > this file > other docs.
- Avoid destructive changes without approval (mass moves/deletes, git resets).

- Architectural patterns in use:
  - Domain-Driven Design
  - Clean Architecture
  - CQRS
- External systems:
  - Database: PostgreSQL 16
  - Message Queue: RabbitMQ and Kafka (switchable)
- Presentation layer projects default to containerized deployment.

## Folder Structure

| Path                              | Purpose                                   |
|-----------------------------------|-------------------------------------------|
| `./.gemini`                       | Gemini CLI settings                        |
| `./.github`                       | GitHub & Copilot resources                 |
| `./docker-compose`                | Compose files and deployment configs       |
| `./docs`                          | Docs and additional design notes           |
| `./https`                         | HTTP files for quick API testing           |
| `./https/<Context>`               | HTTP files for a specific Bounded Context  |
| `./memory`                        | AI agent working memory                    |
| `./scripts`                       | Spec-kit helper scripts                    |
| `./specs`                         | Specs for Spec-Driven Development          |
| `./sql-script`                    | Database scripts                           |
| `./src`                           | .NET source code                           |
| `./src/BC-Contracts`             | Cross-context contracts (MQ payloads)      |
| `./src/BuildingBlocks`           | Foundational building blocks               |
| `./src/Shared`                    | Shared domain kernel                       |
| `./src/<DomainName>`             | Specific domain                            |
| `./src/<DomainName>/DomainCore`  | Domain core (domain/app/infra projects)    |
| `./src/<DomainName>/Presentation`| Presentation projects (WebApi/Consumer)    |
| `./templates`                     | Templates used by spec/plan/task flows     |
| `./tests`                         | Test projects (xUnit, k6, etc.)            |

## Project Rules

| Layer         | Responsibility                       | Naming                           | Location                          |
|---------------|--------------------------------------|----------------------------------|-----------------------------------|
| Domain        | Domain model                          | `<DomainName>.Domains`           | `./src/<DomainName>/DomainCore`   |
| Application   | Application services                  | `<DomainName>.Applications`      | `./src/<DomainName>/DomainCore`   |
| Infrastructure| Technical infrastructure              | `<DomainName>.Infrastructure`    | `./src/<DomainName>/DomainCore`   |
| Presentation  | Web API                               | `<DomainName>.WebApi`            | `./src/<DomainName>/Presentation` |
| Presentation  | Queue Consumer                        | `<DomainName>.Consumer`          | `./src/<DomainName>/Presentation` |
|               | Cross BC Contract                     | `Lab.MessageSchemas.<Domain>`    | `./src/BC-Contracts`              |
|               | Building Blocks                       | `Lab.BuildingBlocks.<layer>`     | `./src/BuildingBlocks`            |
|               | Tests                                 | `<TargetProject>.Tests`          | `./tests`                         |

## Implementation Rules
- Use plural names for folders within projects.
- Solution folders in `.slnx` mirror real directories (except `tests`).
- Prefer `this.` usage.
- DTO naming:
  - In `<DomainName>.WebApi`: input `*Request`, output `*Response`.
  - In `<DomainName>.Application`: input `*Input`, output `*Output`.
- Public APIs require XML summaries written in Traditional Chinese (Taiwan usage).

## Branch Naming
- Feature branches: `NNN-short-desc` (e.g., `001-init-service`).
- `scripts/common.sh` enforces `^[0-9]{3}-` prefix; non-compliant branches will fail certain scripts.
- Keep names aligned with the structure above.

## Workflow (AI & Human)
1) Define scope: service name (e.g., Invoices), context folder (e.g., `Invoice`), layers to create.
2) Create projects at correct paths, e.g.:
   - `dotnet new webapi -n Invoices.WebApi -o src/Invoice/Presentation/Invoices.WebApi`
   - `dotnet new classlib -n Invoices.Applications -o src/Invoice/DomainCore/Invoices.Applications`
3) Add to solution and solution folders:
   - `dotnet sln add src/Invoice/Presentation/Invoices.WebApi/Invoices.WebApi.csproj --solution-folder "Invoice/Presentation"`
4) Provide DI extensions in each project (e.g., `AddApplicationServices`, `AddInfrastructureServices`).
5) Executables include multi-stage `Dockerfile`; add services to `docker-compose/docker-compose.yml` when needed.

## CQRS & Wolverine
- Commands/Queries/Events should be immutable (recommend `record`) with action-first naming (e.g., `CreateOrder`).
- Handlers remain small and focused; avoid infra details inside handlers (use injected services).
- Event processing must consider at-least-once delivery and idempotency; check duplicates before external I/O.
- Publishing/subscription:
  - Prefer Domain Events within a bounded context.
  - Use Integration Events across contexts (kept in `BC-Contracts`).
- Transaction boundaries: align state changes with persistence consistency (Outbox/Inbox if adopted).
- Use WolverineFx for publishing/handling Commands/Queries/Events.
- Naming and placement:
  - Command + its Handler in the same `.cs` file; file named by the Command.
  - Query + its Handler in the same `.cs` file; file named by the Query.
  - Events/Handlers:
    - Domain Events → `<DomainName>.Domains/DomainEvents`.
    - Domain Event Handlers → `<DomainName>.Applications/DomainEventHandlers`.
    - Integration Event Handlers → `<DomainName>.Consumer/IntegrationEventHandlers`.

## BC-Contracts & Versioning
- Changes:
  - Backward-compatible → extend with optional fields.
  - Breaking changes → publish a new schema version; keep old readable for a grace period.
- Namespace: `Lab.MessageSchemas.<DomainName>` with explicit version separation.
- Tests: every contract change requires producer/consumer contract tests.
- Location: Integration Events → `Lab.MessageSchemas.<DomainName>/IntegrationEvents`.

## Build/Run & Broker
- Build at repo root: `dotnet restore` && `dotnet build`.
- Run API/Consumer: `dotnet run --project <path-to-csproj>`.
- Broker selection via env var: `QUEUE_SERVICE=Kafka|RabbitMQ` and matching `ConnectionStrings__KafkaBroker` or `ConnectionStrings__MessageBroker`.
- Local stack: `docker-compose -f ./docker-compose/docker-compose.yml up -d`.

## Code Style
- Follow `.editorconfig`: spaces, CRLF, 150 columns; `System` before other `using`s; namespace aligns to folders; prefer file-scoped namespaces; allow top-level statements.
- Naming: interfaces `I*`; types/methods/properties PascalCase; instance fields `_camelCase`.

## Testing
- Default xUnit. Place test projects under `tests/*/*.Tests.csproj` (e.g., `tests/SaleProducts.Domains.Tests`); class names `<TypeName>Tests`; run with `dotnet test`.
- Test layers (outside-in): Contract → Integration → Unit. Contract or cross-context changes must include Contract/Integration tests.
- Tests should be self-contained; define dependencies in `docker-compose` where needed.
- Events/consumers require idempotency and duplicate-delivery scenarios.

## AI Agents Guidelines
- Plan first:
  - Create a feature and spec: `scripts/create-new-feature.sh "feature description"` → `specs/<branch>/spec.md`.
  - Generate plan skeleton: `scripts/setup-plan.sh` → `plan.md`.
  - Check prerequisites: `scripts/check-task-prerequisites.sh`.
  - Sync agent docs when needed: `scripts/update-agent-context.sh [claude|gemini|copilot]`.
- Change policy: minimal, focused, and aligned with existing structure; avoid unrelated moves/renames.
- Interaction policy:
  - Before large writes or structure changes, update the plan and state expected outputs/paths.
  - Risky ops (deletes, large refactors, dep upgrades, network/keys) require approval or alternatives.
- Validation policy:
  - Run tests closest to changes first, then broaden.
  - Add tests and docs for new functionality (`docs/` or feature folder).
- Toolchain note: `scripts/*` primarily support Gemini CLI and GitHub Copilot; related commands/prompts live in `.gemini/commands/` and `.github/prompts/`. Other agents may ignore tool-specific commands but must follow these guidelines and output locations.

## Docs & Records
- In `specs/<branch>/`, maintain `spec.md`, `plan.md`, and when applicable `contracts/`, `data-model.md`, `quickstart.md`.
- For cross-context contracts or major architectural decisions, add docs in `docs/` (or ADRs if used).
- In PRs, link related specs and attach evidence (logs/screenshots/outputs).

## Commits & PR
- Commits: short imperative messages; optional scope (e.g., `orders: enable Kafka auto-provision`); annotate generators when relevant (e.g., “by gemini cli”).
- PRs: explain motivation, linked issues, impacted services/projects; provide evidence (Scalar/Kafka/RabbitMQ screenshots or logs); use `.github/pull_request_template.md`.

## Scripts & Commands Quickref
- New feature: `scripts/create-new-feature.sh "desc"`
- Plan skeleton: `scripts/setup-plan.sh`
- Check plan/docs: `scripts/check-task-prerequisites.sh`
- Update agent context: `scripts/update-agent-context.sh [claude|gemini|copilot]`
- Build: `dotnet restore && dotnet build`
- Run API/Consumer: `dotnet run --project <csproj>`
- Local stack: `docker-compose -f ./docker-compose/docker-compose.yml up -d`

## Security & Config
- Use env vars or user secrets; avoid committing sensitive data.
- UIs: Kafka `http://localhost:19000`, RabbitMQ `http://localhost:15672` (guest/guest, dev only).
- Broker selection: `QUEUE_SERVICE=Kafka|RabbitMQ`
- Connection strings: `ConnectionStrings__KafkaBroker` or `ConnectionStrings__MessageBroker`

