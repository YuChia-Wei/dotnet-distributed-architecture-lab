# DTO Templates (.NET)

This folder provides DTO templates used for data transfer between layers.

## Contents

- `PlanDto.cs` - Basic DTO template
  - Fluent setters
  - Collection initialization
- `ProjectDto.cs` - Nested DTO template
  - Parent-child relationships
  - Derived counts
- `TaskDto.cs` - Complex DTO template
  - Mixed data types
  - Optional fields
  - Enums and collections

## DTO Design Rules

### 1. Single Responsibility
DTOs carry data only. No domain behavior.

```csharp
public sealed class PlanDto
{
    public string Id { get; private set; } = string.Empty;
    public string Name { get; private set; } = string.Empty;
}
```

### 2. No Domain Dependencies
DTOs must not reference entities or value objects.

```csharp
// BAD: includes domain types
public sealed class TaskDto
{
    public Task Task { get; private set; } = null!;
}

// GOOD: uses primitives
public sealed class TaskDto
{
    public string TaskId { get; private set; } = string.Empty;
}
```

### 3. Fluent Setters
Use fluent setters for readability.

```csharp
var dto = new TaskDto()
    .SetId("task-1")
    .SetName("Implement feature")
    .SetStatus(TaskDto.TaskStatus.InProgress);
```

## DTO vs Entity vs Value Object

| Feature | DTO | Entity | Value Object |
|--------|-----|--------|--------------|
| Purpose | Data transfer | Business entity | Domain concept |
| Mutability | Mutable | Mutable | Immutable |
| Identity | None | Has ID | Value-based |
| Logic | None | Has | Has |

## DTO Structure Patterns

### 1. Basic Structure
```csharp
public sealed class BasicDto
{
    public string Id { get; private set; } = string.Empty;

    public BasicDto SetId(string id)
    {
        Id = id;
        return this;
    }
}
```

### 2. Collections
```csharp
public sealed class CollectionDto
{
    private readonly List<ItemDto> _items = new();
    public IReadOnlyList<ItemDto> Items => _items;

    public CollectionDto AddItem(ItemDto item)
    {
        _items.Add(item);
        return this;
    }
}
```

### 3. Optional Fields
```csharp
public sealed class OptionalFieldDto
{
    public string RequiredField { get; private set; } = string.Empty;
    public string? OptionalField { get; private set; }
    public List<string> Tags { get; private set; } = new();
}
```

## Serialization Notes

If you need JSON attributes, use System.Text.Json:

```csharp
using System.Text.Json.Serialization;

public sealed class SerializableDto
{
    [JsonPropertyName("plan_id")]
    public string PlanId { get; private set; } = string.Empty;
}
```

## Validation Notes

Use DataAnnotations or FluentValidation in the API layer:

```csharp
using System.ComponentModel.DataAnnotations;

public sealed class ValidatedDto
{
    [Required]
    [StringLength(100, MinimumLength = 1)]
    public string Name { get; private set; } = string.Empty;
}
```

## Common Mistakes

- Public fields without encapsulation.
- Inheritance for DTOs (prefer composition).
- Circular references between DTOs.

## Data Flow

```
Controller -> DTO -> UseCase -> Entity -> Repository
    ^                                      |
    +-------------- DTO <- Mapper <--------+
```

## Related Resources
- `../mapper/README.md`
- `../usecase/README.md`
- `../controller/README.md`
