# Reactor Pattern Guide (.NET)

## Context
Reactors are event handlers in the Use Case layer for:
- Cross-aggregate eventual consistency
- Read model projections (CQRS)
- Event transformation (internal -> external)
- Integration side effects

Use Wolverine for message handling and ezDDD concepts for events.

## Key Rules

1. Reactor interface handles `DomainEventData`.
2. Naming:
   - Interface: `When[Event][Reaction]Reactor`
   - Implementation: `[Reaction]When[Event]Service`
3. Place interfaces under `UseCase/Port/In/Reactor`.
4. Keep handlers idempotent.
5. Do not use base test classes.

## Interface Template

```csharp
public interface When[Event][Reaction]Reactor : IReactor<DomainEventData>
{
}
```

## Handler Template (Wolverine)

```csharp
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

    public async Task Handle(DomainEventData message, CancellationToken ct)
    {
        if (message == null)
        {
            return;
        }

        var domainEvent = DomainEventMapper.ToDomain(message);
        if (domainEvent is [Source]Events.[Event] typed)
        {
            await When[Event](typed, ct);
        }
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

TODO: Replace `DomainEventMapper`, `IReactor`, and repository interfaces
with actual ezDDD .NET implementations once available.

## Testing Strategy (BDDfy + xUnit)

- Create BDDfy scenarios (Gherkin-style naming) for:
  - Relevant event triggers expected action
  - Irrelevant events are ignored
- Use fixture-based DI to register the reactor and dependencies.
- Use NSubstitute for external services.

## Common Pitfalls

- Handling `DomainEvent` instead of `DomainEventData`
- Forgetting idempotency checks
- Hardcoding profiles in tests
- Using base test classes (disallowed)

## Verification Checklist

- [ ] Interface uses `DomainEventData`
- [ ] Handler is idempotent
- [ ] No base test classes used
- [ ] Tests cover positive and negative paths
