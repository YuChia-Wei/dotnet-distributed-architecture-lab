# Building Blocks Class Index (Conceptual Layer)

This is a **conceptual design** class index for the .NET Building Blocks and describes target classes for the complete architecture.
This document is a reusable .NET backend building-block reference; it does not claim that the framework repository implements these types.

If a target repo needs an implementation index, `repo-structure-sync` or a documentation workflow must generate it from actual source code rather than copying it from the source template.

> [!NOTE]
> The namespaces below are target design names. Update them when the actual packages are complete.

## Domain Layer Core Classes

```
BuildingBlocks.Domain.DomainEntity<TId>        # Domain entity base (Id + DomainEvents)
BuildingBlocks.Domain.AggregateRoot<TId>       # Aggregate Root base (Version)
BuildingBlocks.Domain.EsAggregateRoot<TId>     # ES Aggregate Root (Apply/When pattern)
BuildingBlocks.Domain.IDomainEvent             # Domain event interface (EventId + OccurredOn)
BuildingBlocks.Domain.IAggregateRoot<TId>      # Aggregate Root interface
BuildingBlocks.Domain.IDomainEntity<TId>       # Entity interface
BuildingBlocks.Domain.ValueObject              # Value Object base (design target)
BuildingBlocks.Domain.InternalDomainEvent      # Internal event (design target)
BuildingBlocks.Domain.DomainEventTypeMapper    # Event type mapping (design target)
```

## Use Case Layer Core Classes

```
BuildingBlocks.Application.Cqrs.Input
BuildingBlocks.Application.Cqrs.ExitCode
BuildingBlocks.Application.Cqrs.UseCaseFailureException
BuildingBlocks.Application.Cqrs.Command
BuildingBlocks.Application.Cqrs.CqrsOutput
```

## Repository Pattern Classes

```
BuildingBlocks.Domain.IAggregateRepository<TAggregate, TId> # Aggregate Root Repository (FindByIdAsync/SaveAsync)
BuildingBlocks.Domain.IDomainRepository<TAggregate, TId>    # Legacy-product compatibility alias; must inherit IAggregateRepository
BuildingBlocks.Application.Queries.IQueryRepository         # Read-only Query Port marker
BuildingBlocks.Application.Repositories.IAggregatePurgePort<TAggregate, TId> # Restricted physical deletion capability
BuildingBlocks.Application.Repositories.IUnitOfWork          # Explicit strongly consistent transaction boundary
BuildingBlocks.Application.Repositories.OutboxRepository     # Only when selected by the target technology configuration
BuildingBlocks.Application.Repositories.IOutboxData
BuildingBlocks.Application.Repositories.IOutboxMapper
BuildingBlocks.Application.Repositories.IRepositoryPeer
BuildingBlocks.Application.Repositories.IStoreData
```

The portable core does not define general writable CRUD or a standard batch repository. If measured needs lead a target repo to create a batch port, it must also define chunking, concurrency, failure, domain-event, and outbox semantics.

## Query Pattern Classes

```
BuildingBlocks.Application.Queries.IQuery
BuildingBlocks.Application.Queries.IQueryRepository
BuildingBlocks.Application.Queries.IProjection
BuildingBlocks.Application.Queries.IProjectionInput
BuildingBlocks.Application.Queries.IArchive
```

## Domain Event Data Classes

```
BuildingBlocks.Application.Events.DomainEventData
BuildingBlocks.Application.Events.DomainEventMapper
BuildingBlocks.Application.Events.ExternalDomainEvent
BuildingBlocks.Application.Events.ExternalDomainEventDto
BuildingBlocks.Application.Events.InternalDomainEventDto
```

## Messaging Classes

```
BuildingBlocks.Messaging.MessageProducer
BuildingBlocks.Messaging.PostEventFailureException
```

## Reactor Pattern Classes

```
BuildingBlocks.Application.Reactors.IReactor
BuildingBlocks.Application.Reactors.IGenericReactor
```

## Outbox Infrastructure Classes (Conditional)

```
BuildingBlocks.Infrastructure.Outbox.OutboxRepositoryPeer
BuildingBlocks.Infrastructure.Outbox.OutboxStore
BuildingBlocks.Infrastructure.Outbox.OutboxClient
BuildingBlocks.Infrastructure.Outbox.OutboxStoreAdapter
BuildingBlocks.Infrastructure.Outbox.EfCoreOutboxClient
BuildingBlocks.Infrastructure.Outbox.IOrmClient
```

These Outbox/ORM classes apply only when the target repository selects the corresponding implementation. This framework does not prescribe a database, ORM, or messaging package.

## InMemory Infrastructure Classes

### Outbox InMemory Support
```
BuildingBlocks.Infrastructure.Outbox.InMemoryOrmDb
BuildingBlocks.Infrastructure.Outbox.InMemoryOrmClient
```

### Event Store InMemory Support
```
BuildingBlocks.Infrastructure.EventStore.InMemoryMessageDb
BuildingBlocks.Infrastructure.EventStore.InMemoryMessageDbClient
```

### Message Broker InMemory Support
```
BuildingBlocks.Messaging.InMemoryMessageBroker
BuildingBlocks.Messaging.InMemoryMessageProducer
BuildingBlocks.Messaging.InMemoryProducer
BuildingBlocks.Messaging.InMemoryConsumer
BuildingBlocks.Messaging.InternalInMemoryMessageConsumer
BuildingBlocks.Messaging.ExternalInMemoryMessageConsumer
```

## Event Sourcing Infrastructure Classes

```
BuildingBlocks.Application.Repositories.EsRepository
BuildingBlocks.Application.Repositories.EventStoreData
BuildingBlocks.Application.Repositories.EventStoreMapper
BuildingBlocks.Infrastructure.EventStore.EsRepositoryPeer
BuildingBlocks.Infrastructure.EventStore.EventStore
BuildingBlocks.Infrastructure.EventStore.MessageDbClient
BuildingBlocks.Infrastructure.EventStore.MessageData
BuildingBlocks.Infrastructure.EventStore.CatchUpRelay
BuildingBlocks.Infrastructure.EventStore.VolatileRelay
BuildingBlocks.Infrastructure.EventStore.MessageDbToDomainEventDataConverter
```

## Testing Support Classes (BDDfy)

```
TestStack.BDDfy.BDDfyExtensions
TestStack.BDDfy.Xunit.BddfyFactAttribute
```

## Design by Contract Classes (uContract)

```
UContract.Contract
UContract.PreconditionViolationException
UContract.PostconditionViolationException
```

## Utility Classes

```
BuildingBlocks.Common.Converter
BuildingBlocks.Infrastructure.OptimisticLockingFailureException
```

## Usage

1. **Find a class**: Use Ctrl+F to search for the class name.
2. **Confirm the namespace**: Copy the full path into a using directive.
3. **Avoid guessing**: If it does not exist, verify it in the Building Blocks project.

## Important Notes

### Concept vs Implementation
- 📘 This document is a **conceptual design** index covering the complete architecture target.
- 📗 Implemented classes in a target repo require a separate implementation index based on actual source code.
- ✅ `BuildingBlocks.*` is provisional naming and does not represent final packages.

### Common Incorrect Paths (Avoid)
- ❌ `DomainModel.*` → ✅ `BuildingBlocks.Domain.*`
- ❌ `Infrastructure.Common.*` → ✅ `BuildingBlocks.Infrastructure.*`
- ❌ `EventSourcingAggregate` → ✅ `EsAggregateRoot`

### Reactor Interface Usage
```csharp
public interface MyReactor : IReactor<DomainEventData>
{
}
```

### InMemory Repository Configuration Example (Illustrative)
```csharp
public static IServiceCollection AddInMemoryRepositories(this IServiceCollection services)
{
    services.AddSingleton<InMemoryOrmDb<ProductData>>();
    services.AddSingleton<InMemoryMessageDb>();
    services.AddSingleton<InMemoryMessageDbClient>();
    return services;
}
```
