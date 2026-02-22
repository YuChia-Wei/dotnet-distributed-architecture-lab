# Mapper Patterns (.NET)

## Overview

Mapper patterns translate objects between layers:
- Domain -> Data (persistence models)
- Data -> Domain (rebuild aggregates)
- Domain -> DTO (API responses)
- Data -> DTO (read models)

In Clean Architecture, mappers keep conversion logic isolated and explicit.

## Mapper Types

### Aggregate Mapper
- Exposes `NewMapper()` for outbox or repository integration.
- Handles domain events and versioning.
- Converts nested entities.

### Entity Mapper
- No `NewMapper()` method.
- Local conversions only.

## Aggregate Mapper Template (C#)

```csharp
public static class PlanMapper
{
    public static PlanData ToData(Plan plan) { /* ... */ }
    public static Plan ToDomain(PlanData data) { /* ... */ }
    public static PlanDto ToDto(Plan plan) { /* ... */ }

    private static readonly IOutboxMapper<Plan, PlanData> Mapper = new MapperImpl();
    public static IOutboxMapper<Plan, PlanData> NewMapper() => Mapper;
}
```

## Entity Mapper Template (C#)

```csharp
public static class TaskMapper
{
    public static TaskData ToData(Task task) { /* ... */ }
    public static Task ToDomain(TaskData data) { /* ... */ }
    public static TaskDto ToDto(Task task) { /* ... */ }
}
```

## Best Practices

1. Use static methods (no mapper instances).
2. Always check nulls.
3. Provide batch conversion helpers.
4. For event sourcing, set stream name, event data, and timestamps.
5. Clear domain events after rebuild to avoid re-persisting.

## Common Mistakes

- Entity mappers exposing outbox mapper (only aggregate mappers should).
- Forgetting event sourcing metadata.
- Using raw constructors instead of `ValueOf(...)`.

## Related Resources
- `../aggregate/README.md`
- `../dto/README.md`
