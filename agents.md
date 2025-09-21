# Repository Guidelines

## Scope & Precedence
- This document serves as the collaboration guideline for AI agents and humans across the entire repository.
- If a subdirectory has another AGENTS.* file, the deeper one takes precedence.
- Command priority: User/Approval > Subfolder AGENTS > This file > Other general documents.
- Avoid large-scale refactoring and destructive operations (deleting files, moving many files, git reset) unless necessary.

## Technical Background
- **Language/Version**: C# 13, .NET 9
- **Primary Dependencies**:
  - **Message Handling**: Wolverine.NET
  - **Persistence**: Dapper, Npgsql
  - **Web Api Servers**: ASP.NET Core
  - **Queues Consumer Programs**: Console App
  - **Message Bus**: RabbitMQ and Kafka
- **Database**: PostgreSQL 16
- **Testing**: xUnit
- **Target Platform**: Linux container (via Docker)
- **Constraints**:
  - Cross-domain data synchronization allows for "eventual consistency".
  - The entire system is designed using the Domain-Driven Design pattern.
  - The software architecture adopts Clean Architecture.
  - Uses CQRS.
  - Cross-domain services are not allowed to communicate via web APIs; they can only interact using a message queue mechanism.

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