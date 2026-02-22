# AI Prompt for Reactor Generation (.NET)

## Context
Generate reactors for eventual consistency using:
- Clean Architecture
- DDD
- CQRS
- Event Sourcing
- Wolverine for message handling
- ezDDD concepts (to be implemented in .NET)

## Reactor Interface Definition (ADR-018 Equivalent)

The reactor interface must handle `DomainEventData`:
```csharp
public interface When[Event][Reaction]Reactor : IReactor<DomainEventData>
{
}
```

## File Structure Pattern

### 1. Reactor Interface
Path:
`src/[Aggregate]/UseCase/Port/In/Reactor/When[Event][Reaction]Reactor.cs`

```csharp
namespace [RootNamespace].[Aggregate].UseCase.Port.In.Reactor;

public interface When[Event][Reaction]Reactor : IReactor<DomainEventData>
{
}
```

### 2. Service Implementation
Path:
`src/[Aggregate]/UseCase/Service/Reactor/[Reaction]When[Event]Service.cs`

```csharp
using [RootNamespace].[Aggregate].UseCase.Port.In.Reactor;
using [RootNamespace].[Aggregate].UseCase.Port.Out.Inquiry;
using [RootNamespace].[Aggregate].Entity;
using [RootNamespace].Shared.Contracts;

public sealed class [Reaction]When[Event]Service : When[Event][Reaction]Reactor
{
    private readonly IFind[Entity]By[Criteria]Inquiry _inquiry;
    private readonly IRepository<[Aggregate], [Aggregate]Id> _repository;

    public [Reaction]When[Event]Service(
        IFind[Entity]By[Criteria]Inquiry inquiry,
        IRepository<[Aggregate], [Aggregate]Id> repository)
    {
        Contract.RequireNotNull(nameof(inquiry), inquiry);
        Contract.RequireNotNull(nameof(repository), repository);
        _inquiry = inquiry;
        _repository = repository;
    }

    public Task Handle(DomainEventData message, CancellationToken ct)
    {
        if (message == null)
        {
            return Task.CompletedTask;
        }

        var domainEvent = DomainEventMapper.ToDomain(message);
        if (domainEvent is [Source]Events.[Event] typed)
        {
            return When[Event](typed, ct);
        }

        return Task.CompletedTask;
    }

    private async Task When[Event]([Source]Events.[Event] @event, CancellationToken ct)
    {
        var ids = await _inquiry.FindBy[Criteria]Async(@event.[criteria](), ct);

        foreach (var id in ids)
        {
            var entity = await _repository.FindByIdAsync(id, ct);
            if (entity != null)
            {
                entity.[action](@event.UserId);
                await _repository.SaveAsync(entity, ct);
            }
        }
    }
}
```

### 3. Test Case
Use the test generation template (`test-case-full.md`).

## Notes

- Use `DomainEventData` as the message type.
- Keep idempotency checks inside the handler.
- Use Wolverine handler conventions (Task Handle).
- TODO: finalize ezDDD .NET interfaces and mapper APIs.
