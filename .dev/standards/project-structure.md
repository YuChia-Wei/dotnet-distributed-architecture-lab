# Conditional .NET Backend Project Structure Profile

This document is a reusable target-repository profile, not the observed directory
structure of this AI context framework. Apply its physical layout and naming only
when repository evidence or an explicit team decision adopts them. Run
`repo-structure-sync` first when this framework is copied into a target repository;
unconfirmed paths and project names must remain unresolved.

The normative invariants are DDD and Clean Architecture dependency direction,
port-and-adapter boundaries, and MQ-based cross-bounded-context integration. The
multi-BC tree, `DomainCore` / `Presentation` grouping, shared-project taxonomy,
project-name examples, and `.slnx` organization below are conditional profile
defaults or examples rather than universal requirements.

## Project Directory Structure

```
project-root/
├── src/
│   ├── BC-Contracts/                    # Cross-BC communication contracts (Published Language)
│   │   └── <Company>.BoundedContextContracts.<Domain>/ # Example contract project
│   ├── BuildingBlocks/                  # Shared building blocks (architectural infrastructure)
│   │   ├── <Company>.BuildingBlocks.Domain/   # Example shared components
│   │   ├── <Company>.BuildingBlocks.Application/
│   │   └── <Company>.BuildingBlocks.Infrastructure/
│   ├── Shared/                          # Shared domain core (Shared Kernel)
│   │   └── <Company>.SharedKernel/       # Example shared domain concepts
│   └── <DomainName>/                    # Specific Domain (for example, Order or Product)
│       ├── DomainCore/                  # Domain core layer
│       │   ├── <DomainName>.Domains/        # Domain Model
│       │   ├── <DomainName>.Applications/   # Application layer
│       │   └── <DomainName>.Infrastructure/ # Technical infrastructure
│       └── Presentation/                # Presentation layer
│           ├── <DomainName>.WebApi/         # REST API
│           └── <DomainName>.Consumer/       # MQ Consumer (Console App)
├── tests/
│   └── <TargetProject>.Tests/           # Tests for the corresponding project
├── docker-compose/                      # Docker Compose configuration
├── docs/                                # Documentation and design notes
├── https/                               # HTTP test files
│   └── <Context>/                       # HTTP tests for a specific BC
├── sql-script/                          # Database scripts
├── .ai/                                 # Canonical reusable AI assets
├── .agents/skills/                      # Current-runtime thin skill wrappers
├── .claude/skills/                      # Claude-compatible thin skill wrappers
├── .dev/                                # Project truth, standards, guides, and workflows
├── .github/                             # GitHub repository resources; the Copilot adapter is optional
└── *.slnx                               # .NET Solution
```

## Conditional Physical Layout

The following names and locations apply only when the target adopts this profile.
Other physical layouts are valid when they preserve the normative dependency and
port/adapter rules and are recorded in target repository evidence.

| Layer | Responsibility | Naming Convention | Location |
|------|------|---------|------|
| Domain | Domain Model | `<DomainName>.Domains` | `./src/<DomainName>/DomainCore` |
| Application | Use Cases and ports | `<DomainName>.Applications` | `./src/<DomainName>/DomainCore` |
| Infrastructure | Technical infrastructure | `<DomainName>.Infrastructure` | `./src/<DomainName>/DomainCore` |
| Presentation | Web API | `<DomainName>.WebApi` | `./src/<DomainName>/Presentation` |
| Presentation | Queue Consumer | `<DomainName>.Consumer` | `./src/<DomainName>/Presentation` |
| Cross-BC | Cross-BC communication contracts | `<Company>.BoundedContextContracts.<Domain>` | example: `./src/BC-Contracts` |
| BuildingBlocks | Business-neutral contracts plus narrowly justified mechanics | `<Company>.BuildingBlocks.<Layer>` | example: `./src/BuildingBlocks` |
| SharedKernel | Shared domain core | `<Company>.SharedKernel` | example: `./src/Shared` |
| Tests | Test project | `<TargetProject>.Tests` | `./tests` |

## Documentation and AI Asset Responsibilities

| Path | Primary Audience | Purpose |
|------|---------|------|
| `./.dev/guides/ai-collaboration-guides` | Human | AI collaboration guides, workflows, and prompt templates |
| `./.dev/guides` | Human | General development and design guides (AI collaboration / design / implementation / learning) |
| `./.ai` | Agent | Canonical reusable AI assets, skill specs, shared rules, and context scripts |
| `./.agents/skills` | Agent | Current-runtime thin wrappers pointing to canonical skill specs |
| `./.claude/skills` | Agent | Claude-compatible thin wrappers pointing to canonical skill specs |

## Conditional Solution File (`.slnx`) Profile

Apply these grouping conventions only when the target repository uses `.slnx` and
explicitly adopts this profile.

- Solution Folders in `.slnx` use logical grouping and do not need to match the physical directory structure.
- Solution Folder names use leading and trailing slashes.
- Product projects use one logical grammar:
  `/<workload>/DomainCore/` and `/<workload>/Presentation/`.
- `tests` may remain a single top-level group: `/tests/`.

### Workload Mapping

Rule ID: `PROJECT-GRAMMAR-001` (`profile-default`).

`workload` is a logical solution-navigation boundary, not a universal physical
directory name:

| Repository profile | `workload` means | Typical count | Example logical folders |
| --- | --- | --- | --- |
| micro-system / mini-system mono repo | one Bounded Context | one or more | `/Orders/DomainCore/`, `/Orders/Presentation/` |
| mono-system repository | the system represented by the repository | normally one | `/Commerce/DomainCore/`, `/Commerce/Presentation/` |

This mapping gives both profiles the same development navigation:

- `DomainCore` groups Domain, Application, and Infrastructure projects that
  realize the workload's business capability;
- `Presentation` groups runtime inbound adapters such as Web API, gRPC, worker,
  and MQ Consumer projects;
- tests, analyzers/tooling, BuildingBlocks, Shared Kernel, Published Language,
  and CrossCutting projects may remain explicit top-level capability groups;
- a target may retain a flat physical `src/` layout while using the logical
  `.slnx` grammar.

Do not create artificial Bounded Context folders in a mono-system repository
only to imitate a micro-system repo. Conversely, do not collapse real Bounded
Contexts in a micro-system mono repo into one layer-first solution view.

### Downstream Profile Comparison

| Evidence repository | Observed organization | Mapping to the shared grammar | Disposition |
| --- | --- | --- | --- |
| `dotnet-mq-arch-lab` | Bounded Context folders such as `Order/DomainCore` and `Order/Presentation` | each Bounded Context is one workload | direct evidence for the micro-system profile |
| `dotnet-webapi-lab` | numeric layer-first folders (`Domain`, `Application`, `Infrastructure`, `Presentation`) | the repository/system is one workload; layer projects map under its `DomainCore` or `Presentation` group | useful mono-system evidence, but numeric prefixes and physical layout are not canonical |

The downstream repositories are evidence only. Targets do not need their names,
prefixes, or exact project counts.

### Review Checklist

- [ ] Every product project belongs to one workload or an explicit shared
      capability group.
- [ ] Each workload has a logical `DomainCore` and/or `Presentation` group as
      applicable.
- [ ] Domain, Application, and Infrastructure libraries are under
      `DomainCore`; runtime inbound adapters are under `Presentation`.
- [ ] The logical grouping does not change Clean Architecture dependency
      direction.
- [ ] The selected workload mapping is recorded in target repository evidence.
- [ ] Physical directories are not rewritten solely to match solution folders.
- [ ] CrossCutting runtime/AOP observability is outside Domain, and Domain has no
      dependency on it.

The last item is the only Observability boundary in this standard. Detailed
attribute behavior, redaction, async interception, package selection, and
validation remain in backlog item `OBS-001` for a separate design workflow.

## Application-Layer Directory Structure

```
<DomainName>.Applications/
├── UseCases/                    # Application inbound ports + implementations
│   ├── Create<Entity>/
│   │   ├── ICreate<Entity>UseCase.cs
│   │   ├── Create<Entity>UseCase.cs
│   │   ├── Create<Entity>Input.cs
│   │   └── Create<Entity>Output.cs
│   └── Get<Entity>/
│       ├── IGet<Entity>UseCase.cs
│       ├── Get<Entity>UseCase.cs
│       └── Get<Entity>Output.cs
├── Ports/                       # Outbound port interface definitions
│   ├── Queries/
│   │   └── I<Feature>QueryRepository.cs
│   ├── Persistence/             # Include only domain-specific capabilities
│   │   └── I<Capability>Port.cs
│   ├── Messaging/
│   │   └── I<Feature>EventPublisher.cs
│   └── I<Feature>QueryService.cs # optional composition port
├── QueryServices/               # Optional Application query composition
│   └── <Domain>QueryService.cs
├── Dispatch/                    # Optional package-neutral dispatch contracts/handlers
│   └── Create<Entity>Command.cs
├── DomainEventHandlers/         # Domain Event handlers
└── Dtos/                        # Application-layer DTOs (Input/Output)
```

The portable Aggregate Repository contract resides in `BuildingBlocks.Application`:

- `IAggregateRepository<TAggregate, TId>`
- compatibility `IDomainRepository<TAggregate, TId>`
- `IQueryRepository` marker

Do not create an empty `I<Aggregate>Repository` for every Aggregate by default. Create a domain-specific port only to maintain compatibility with existing code or to add approved Aggregate lifecycle/capability semantics.

### Application Terminology and Responsibilities

- `Use Case`
  - An explicit inbound port and application orchestration object, such as
    `ICreateProductUseCase` / `CreateProductUseCase`
- `Command` / `Query`
  - A delivery contract needed only for a dispatch entry, not a Use Case input
- `Handler`
  - An inbound adapter for a real dispatch/message entry that maps input and then invokes one Use Case
- `Application Service`
  - Not defined by this standard; if a target repository uses one, its responsibility must be decided explicitly elsewhere

Default rules:

- Controllers directly inject Use Case interfaces.
- Use Case implementations use the `*UseCase` suffix and `ExecuteAsync`.
- A Handler and a Use Case are distinct objects.
- Do not create a Handler without a real dispatch/message entry.
- Place Wolverine/MediatR/MQ-specific Handlers in an inbound adapter or composition
  boundary, not in a portable Use Case.
- Only explicitly approved pure-query endpoints may directly access a Query Repository/Service as an exception.

Recommended relationship chain:

```text
Controller
  -> I<Operation>UseCase
  -> <Operation>UseCase
  -> Aggregate / Domain Service / Repository / Query Service
  -> Use Case Output
```

Actual dispatch/message entry:

```text
Command / Message
  -> Handler
  -> I<Operation>UseCase
```

For additional rules, see [`USECASE-COMMAND-HANDLER-RELATIONSHIP.MD`](./USECASE-COMMAND-HANDLER-RELATIONSHIP.MD).

## Infrastructure-Layer Directory Structure

```
<DomainName>.Infrastructure/
├── Repositories/                # Aggregate Repository adapters
│   └── <Aggregate>Repository.cs
├── QueryRepositories/           # Query Repository implementations
│   └── <Feature>QueryRepository.cs
├── Persistence/                 # Target-selected DB/ORM/event-store configuration
├── Writers/                     # Outbox/Projection/Import/Purge capability adapters
└── Messaging/                   # MQ-related implementations
    └── <Feature>EventPublisher.cs # Application outbound port adapter
```

## Clean Architecture Layers

- **Domain**: Aggregates, Entities, Value Objects, Domain Events
- **Application**: Use Cases, inbound/outbound Ports, Policies
- **Infrastructure**: target-selected persistence, Outbox, Message Bus, Repository/Query/Writer adapters
- **Presentation**: Controllers, DTO mapping, validation, MQ Consumers

## Naming and Dependency Direction

- Domain does not depend on any other layer.
- Application depends on Domain.
- Infrastructure depends on Application/Domain.
- Presentation depends on Application (not directly on Infrastructure; connect it through DI).

### Relationship Between Adapters and the Bus

- By default, a Controller depends on a Use Case interface, not on a Handler, bus, dispatcher,
  write repository, or aggregate.
- Only explicitly approved pure-query endpoints may directly depend on a read-only Query Repository/Service.
- A normal synchronous API within the same BC and process directly invokes a Use Case port.
- A dispatch/message Handler exists only when there is a real delivery entry and invokes one Use Case.
- Only cross-BC communication mandates an MQ/message bus.
- A Use Case depends on a project-owned event publisher port; only Infrastructure depends on
  Wolverine or another broker/framework.

### Persistence Port Rules

- An Aggregate Repository accepts only an Aggregate Root.
- Persist a child Entity through its owning Aggregate Root.
- A Query Repository implements `IQueryRepository` and is read-only.
- Use capability-specific ports for physical purge, Outbox, Projection, Import, and similar capabilities.
- Target-specific batch persistence does not belong in the portable/default project template.

## Cross-BC Communication Rules

> ⚠️ **Important restriction**: Cross-Domain services **must not** communicate through Web APIs; they must use a Message Queue (RabbitMQ/Kafka).
> 💡 **Consistency model**: Cross-Domain data synchronization uses **Eventual Consistency** and does not require strong consistency.

| Communication Type | Mechanism | Definition Location |
|---------|---------|---------|
| Within the same BC | Domain Events | `<Domain>.Domains/DomainEvents` |
| Cross-BC | Integration Events | target-selected Published Language contract location; example: `./src/BC-Contracts/<Company>.BoundedContextContracts.<Domain>` |

## Shared Projects Classification

> The DDD concepts and dependency constraints are authoritative. The three-project
> physical split is a conditional profile example and must not be inferred as
> current target-repository truth.

When a target adopts this profile, it may use these three distinct shared areas:

| Project | DDD Concept | Responsibility | Dependency Permission |
|------|---------|------|----------|
| `BuildingBlocks` | Architectural infrastructure | Interfaces without business semantics; optional `EsAggregateRoot<TId>` mechanics only | May be referenced by all layers |
| `SharedKernel` | Shared Kernel | Shared domain concepts across BCs (VOs, Enums) | May be referenced by the Domain layer |
| `BC-Contracts` | Published Language | Communication contracts between BCs (Integration Events, Request/Reply) | **Must not be referenced by the Domain layer** |

### Dependency Direction Constraints

```
BuildingBlocks ← may be referenced by all layers
SharedKernel   ← Domain / Application / Infrastructure / Presentation
BC-Contracts   ← Application / Infrastructure / Presentation (Domain prohibited)
```

### BC-Contracts Internal Categories

| Subdirectory | Purpose | Example |
|--------|------|------|
| `IntegrationEvents/` | Asynchronous event contracts (MQ Payload) | `OrderPlaced`, `ProductStockDecreased` |
| `Interactions/` | Request/Reply contracts | `ReserveInventoryRequestContract` |
| `DataTransferObjects/` | Cross-BC query response contracts | `OrderDetailsResponse` |

When using these areas, ensure that Bounded Context boundary isolation is not compromised.

The default profile does not require `DomainEntity<TId>`, non-ES
`AggregateRoot<TId>`, or `ValueObject` base classes. Normal Aggregates implement
`IAggregateRoot<TId>` directly. See the
[BuildingBlocks Reconstruction Contract](BUILDING-BLOCKS-RECONSTRUCTION-CONTRACT.md)
for the optional executable-tested `EsAggregateRoot<TId>` and target ownership
rules.
