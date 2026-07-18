# BuildingBlocks Contract Index

This is a navigation index for portable dotnet-backend BuildingBlocks contracts.
It is not a catalog of a complete package or a promise that every historical
class should be recreated.

Read the
[BuildingBlocks Reconstruction Contract](../../../../../.dev/standards/BUILDING-BLOCKS-RECONSTRUCTION-CONTRACT.md)
before selecting a type. Target implementations and namespaces remain
target-owned.

Rule ID: `AGGREGATE-ES-001`.

## Active Portable Domain Contracts

| Contract | Default form | Status | Evidence |
| --- | --- | --- | --- |
| `IDomainEntity<TId>` | interface | optional when reusable identity marking is useful | [source include](../source-includes/domain/IDomainEntity.cs) |
| `IAggregateRoot<TId>` | interface | canonical Aggregate marker | [source include](../source-includes/domain/IAggregateRoot.cs) |
| `IDomainEvent` | interface | canonical event marker | [source include](../source-includes/domain/IDomainEvent.cs) |
| `EsAggregateRoot<TId>` | optional abstract class | only approved default-profile base class | [source include](../source-includes/domain/EsAggregateRoot.cs) and [behavior contract](../../../../../.dev/standards/BUILDING-BLOCKS-RECONSTRUCTION-CONTRACT.md#optional-esaggregateroottid-behavior-contract) |

Normal Aggregates implement `IAggregateRoot<TId>` directly. Entities may express
identity directly or implement `IDomainEntity<TId>`. Value Objects prefer
immutable `record` or `record struct` types.

The default profile does not require:

- `DomainEntity<TId>`;
- non-ES `AggregateRoot<TId>`;
- a `ValueObject` base class;
- shared test base classes.

## Active Portable Application Ports

| Contract | Responsibility |
| --- | --- |
| `IAggregateRepository<TAggregate, TId>` | `FindByIdAsync` and `SaveAsync` for one Aggregate boundary |
| `IQueryRepository` | read-only query-port marker |
| `IAggregatePurgePort<TAggregate, TId>` | restricted physical-deletion capability |
| target-named event publisher port | Application-owned outbound integration boundary when messaging is selected |
| target-named transaction port | explicit strongly consistent boundary only when requirements justify it |

`IDomainRepository<TAggregate, TId>` is a compatibility alias only when a target
already owns that name. A generic writable CRUD repository and generic batch
repository are not part of the portable core.

## Target-Selected Implementations

The following are capability categories, not canonical BuildingBlocks classes:

- persistence adapters, ORM clients, event stores, and repository peers;
- Outbox stores and relay implementations;
- message producers, consumers, and broker clients;
- projection, import, archive, and purge writers;
- observability, tracing, metrics, logging, and AOP components;
- in-memory test adapters;
- serialization and event-type mapping implementations.

They belong to product Infrastructure or CrossCutting projects and use names
chosen by the target. Technology selections such as EF Core, Dapper, Wolverine,
Kafka, RabbitMQ, or an observability library must come from target evidence.

## Historical Names

Names such as `Input`, `ExitCode`, `CqrsOutput`, `MessageProducer`,
`OutboxRepositoryPeer`, `InMemoryOrmDb`, `MessageDbClient`, BDDfy, and uContract
originated in Java/EzDDD or lab-specific designs. They may still be useful
concepts, but they are not active canonical type requirements.

Use the provenance matrix in the
[reconstruction contract](../../../../../.dev/standards/BUILDING-BLOCKS-RECONSTRUCTION-CONTRACT.md#provenance-and-concept-disposition)
when deciding whether to retain, rename, or replace one in a target.

## Usage

1. Select the capability from current requirements and architecture decisions.
2. Read the normative standard for its semantics.
3. Prefer an interface or product-owned type.
4. Use `EsAggregateRoot<TId>` only for an event-sourced Aggregate.
5. Treat copied source includes as target-owned and reconcile upgrades through
   `ai-context-upgrader`.
