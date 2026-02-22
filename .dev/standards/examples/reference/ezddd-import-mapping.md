# ezDDD .NET Import Mapping (Reference)

This guide defines the expected .NET type and namespace conventions for ezDDD.
Because ezDDD .NET packages may not exist yet, treat namespaces as placeholders
and update them once the real packages are available.

## Core Concepts (Expected Types)

| Concept | Expected Type Name | Notes |
| --- | --- | --- |
| Entity | `IEntity<TId>` | Entities have identity. |
| Value Object | `IValueObject` | Prefer immutable records. |
| Domain Event | `IDomainEvent` | Public events. |
| Internal Domain Event | `IInternalDomainEvent` | Internal events for aggregate. |
| Aggregate Root | `AggregateRoot<TId, TEvent>` | Non-ES aggregate. |
| ES Aggregate Root | `EsAggregateRoot<TId, TEvent>` | Event-sourced aggregate. |
| Domain Event Mapper | `DomainEventMapper` | Map to/from `DomainEventData`. |
| Domain Event Type Mapper | `DomainEventTypeMapper` | Maps event type names. |

TODO: Replace type names with actual ezDDD .NET types.

## CQRS Concepts

| Concept | Expected Type Name |
| --- | --- |
| Command | `ICommand<TInput, TOutput>` |
| Query | `IQuery<TInput, TOutput>` |
| CQRS Output | `CqrsOutput` |
| Projection | `IProjection<TInput, TResult>` |
| Projection Input | `ProjectionInput` |

## Use Case Layer

| Concept | Expected Type Name |
| --- | --- |
| Input | `IInput` |
| Exit Code | `ExitCode` |
| Use Case Failure | `UseCaseFailureException` |

## Repository and Messaging

| Concept | Expected Type Name |
| --- | --- |
| Repository | `IRepository<T, TId>` |
| Message Bus | `IMessageBus<TMessage>` |
| Domain Event Data | `DomainEventData` |

## Common Mistakes to Avoid

1. Do not mix `DomainEvent` with `DomainEventData`.  
   `DomainEventData` is the serialized transport shape.
2. Do not guess namespaces. Update this doc once ezDDD .NET packages are set.
3. Always keep domain events immutable (record types recommended).
4. Use `DomainEventTypeMapper` for serialization stability.

## Example Usage (Placeholder)

```csharp
// TODO: replace namespaces with actual ezDDD .NET packages.
using EzDdd.Entity;
using EzDdd.Cqrs;
using EzDdd.UseCase;

public sealed record PlanCreated(/* ... */) : IDomainEvent
{
    public IDictionary<string, object> Metadata { get; init; } = new Dictionary<string, object>();
}
```

## Contract Utilities

Use uContract in .NET once available:
```csharp
using static UContract.Contract;
```

TODO: add actual namespace once uContract .NET is created.
