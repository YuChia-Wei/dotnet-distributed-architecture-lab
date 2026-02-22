# Outbox Repository Pattern Implementation Guide (.NET)

## Overview
This guide explains how to implement the Outbox Repository pattern for ezDDD-style aggregates
using EF Core and Wolverine.

## Contents
1. Outbox pattern overview
2. Integration notes (Wolverine + EF Core)
3. Implementation steps
4. Example code
5. Testing requirements
6. Best practices

## Outbox Pattern Overview

### Dual-write problem
When an aggregate is saved and an event is published separately, failures can lead to
inconsistent state:

```csharp
// BAD: dual-write risk
public void CreateOrder(Order order)
{
    _repository.Save(order);
    _bus.Publish(new OrderCreated(order)); // if this fails, state is inconsistent
}
```

### Outbox solution
Write domain data and events in the same transaction, then publish asynchronously:

```csharp
// GOOD: outbox
public void CreateOrder(Order order)
{
    _repository.Save(order);
    _outbox.Save(order.DomainEvents); // same transaction
    // publisher/relay sends events later
}
```

### Flow
```
Repository.save() -> PostgreSQL (domain + outbox)
                     -> Relay/Publisher -> Message Broker -> Reactors/Handlers
```

## Integration Notes (Wolverine + EF Core)

- Use EF Core as the ORM.
- Use Wolverine for outbox durability, messaging, and CQRS handlers.
- Keep ezDDD concepts (domain events, aggregate versioning, invariants).
- TODO: map ezddd-gateway behavior to Wolverine outbox pipelines.

## Implementation Steps

### 1) Define Outbox Entities
Use EF Core entities implementing `IOutboxData<TId>` and mark event fields as not mapped.

See:
- `PlanData.cs`
- `ProjectData.cs`
- `TaskData.cs`

### 2) Implement Outbox Mappers
Provide `ToData` / `ToDomain` mappings and keep an inner outbox mapper.

See:
- `PlanOutboxMapper.cs`
- `ProjectOutboxMapper.cs`
- `TaskOutboxMapper.cs`

### 3) Configure DbContext
Register a dedicated read/write DbContext for outbox storage.

See:
- `PlanDbContext.cs`
- `DataSourceConfig.cs`

### 4) Register Repositories
Wire outbox repositories and Wolverine outbox settings.

See:
- `RepositoryConfig.cs`

## Testing Requirements (Mandatory)

Each outbox repository must include integration tests:
1. Persistence of all fields
2. Read-back integrity
3. Soft-delete behavior
4. Optimistic concurrency/versioning

Use xUnit + BDDfy (Gherkin-style naming) and NSubstitute for mocks.
Refer to the dotnet test examples when implemented (TODO).

## Best Practices

- Clean up published outbox records (retention policy).
- Use retries with backoff for publishing.
- Monitor backlog size and publish latency.
- Keep events idempotent with stable IDs.

## Related Files
- `../bdd-given-when-then-example/OUTBOX-TEST-CONFIGURATION.md`
- `../bdd-given-when-then-example/ProductOutboxRepositoryTests.cs` (TODO)
