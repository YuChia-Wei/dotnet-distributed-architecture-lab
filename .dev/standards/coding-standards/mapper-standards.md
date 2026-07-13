# Mapper Coding Standards (.NET)

This document defines coding standards for Mapper classes that convert data objects between layers.

---

## 📌 Overview

Mappers convert between Domain and DTO/Data objects.

- **Domain → Data**: Convert a domain object to a persistence object
- **Data → Domain**: Convert a persistence object back to a domain object
- **Domain → DTO**: Convert a domain object to a data-transfer object

---

## 🏷️ Pattern Markers (for Automated Checks)

The following markers are used by automated code-review scripts:

```yaml
# Mapper rules
Pattern (required): static class
Pattern (required): ArgumentNullException\.ThrowIfNull

# Forbidden rules
Pattern (forbidden, ignore-comment): I[A-Za-z0-9]*Repository|UseCase|Handler
```

---

## 🔴 Mandatory Rules (MUST FOLLOW)

### 1. Use Static Methods

A Mapper SHOULD use static methods and avoid instance creation:

```csharp
// ✅ Correct: use a static class and static methods
public static class ProductMapper
{
    public static ProductData ToData(Product aggregate)
    {
        ArgumentNullException.ThrowIfNull(aggregate);
        
        return new ProductData
        {
            Id = aggregate.Id.Value,
            Name = aggregate.Name,
            State = aggregate.State.ToString(),
            IsDeleted = aggregate.IsDeleted,
            CreatedAt = aggregate.CreatedAt,
            UpdatedAt = aggregate.UpdatedAt
        };
    }
    
    public static Product ToDomain(ProductData data)
    {
        ArgumentNullException.ThrowIfNull(data);
        
        // Rebuild from Event Sourcing
        if (data.DomainEvents?.Any() == true)
        {
            var events = data.DomainEvents
                .Select(DomainEventMapper.ToDomain)
                .ToList();
            
            var product = new Product(events);
            product.ClearDomainEvents();
            return product;
        }
        
        // Rebuild from current state. Constructor behavior is unknown here,
        // so explicitly remove any events emitted during reconstruction.
        var product = new Product(
            ProductId.From(data.Id),
            data.Name,
            data.CreatorId
        );
        product.ClearDomainEvents();
        return product;
    }
}

// ❌ Incorrect: create a Mapper instance
public class ProductMapper
{
    public ProductData ToData(Product aggregate)  // Not static
    {
        // ...
    }
}
```

---

### 2. Complete Bidirectional Conversion

`ToData()` and `ToDomain()` MUST be symmetrical:

```csharp
// ✅ Correct: ToData serializes; ToDomain deserializes
public static class ProductMapper
{
    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        WriteIndented = false
    };

    public static ProductData ToData(Product aggregate)
    {
        var data = new ProductData
        {
            Id = aggregate.Id.Value,
            Name = aggregate.Name,
            State = aggregate.State.ToString()
        };
        
        // Serialize a complex object
        if (aggregate.DefinitionOfDone is not null)
        {
            data.DefinitionOfDoneJson = JsonSerializer.Serialize(
                aggregate.DefinitionOfDone, JsonOptions);
        }
        
        return data;
    }

    public static Product ToDomain(ProductData data)
    {
        var product = new Product(
            ProductId.From(data.Id),
            data.Name,
            data.CreatorId
        );
        
        // Deserialize a complex object
        if (!string.IsNullOrEmpty(data.DefinitionOfDoneJson))
        {
            var dod = JsonSerializer.Deserialize<DefinitionOfDone>(
                data.DefinitionOfDoneJson, JsonOptions);
            product.DefineDefinitionOfDone(dod);
        }
        
        return product;
    }
}
```

Additional requirements:

- Prefer reusing one `JsonSerializerOptions` instance.
- A complex-object serialization failure SHOULD degrade gracefully rather than make the mapper terminate the entire flow.
- If the data contains domain events, `ToDomain()` SHOULD prefer event-based rebuilding.

---

### 3. The IsDeleted Field MUST Be Mapped

An Aggregate Root Mapper MUST handle the `IsDeleted` field:

```csharp
// ✅ Correct: map the IsDeleted field
public static ProductData ToData(Product aggregate)
{
    return new ProductData
    {
        Id = aggregate.Id.Value,
        Name = aggregate.Name,
        IsDeleted = aggregate.IsDeleted,  // MANDATORY!
        // ...other fields
    };
}

public static Product ToDomain(ProductData data)
{
    var product = new Product(
        ProductId.From(data.Id),
        data.Name,
        data.CreatorId
    );
    
    // MANDATORY: restore IsDeleted state
    if (data.IsDeleted)
    {
        product.MarkAsDeleted();
    }
    
    return product;
}

// ❌ Incorrect: omit IsDeleted mapping
public static ProductData ToData(Product aggregate)
{
    return new ProductData
    {
        Id = aggregate.Id.Value,
        Name = aggregate.Name
        // IsDeleted is missing!
    };
}
```

---

### 4. Domain Events and Metadata MUST Be Mapped

If a mapper participates in a write-model/outbox round trip, it MUST handle:

- domain events
- event metadata
- stream identity (when the aggregate uses the event/outbox model)

```csharp
public static ProductData ToData(Product aggregate)
{
    return new ProductData
    {
        Id = aggregate.Id.Value,
        DomainEventDatas = aggregate.DomainEvents
            .Select(DomainEventMapper.ToData)
            .ToList(),
        StreamName = aggregate.StreamName
    };
}
```

```csharp
public static Product ToDomain(ProductData data)
{
    if (data.DomainEventDatas is { Count: > 0 })
    {
        var events = data.DomainEventDatas
            .Select(DomainEventMapper.ToDomain)
            .Cast<IDomainEvent>()
            .ToList();

        var product = new Product(events);
        product.ClearDomainEvents();
        return product;
    }

    // Fallback: rebuild from current state
}
```

### Pending Domain Events After Reconstruction

An aggregate returned by `ToDomain()` MUST have no pending `DomainEvents`. Rehydration restores historical or persisted state; it does not represent a new business decision and MUST NOT cause those events to be published or persisted again.

- A rehydration constructor SHOULD replay historical events through `When(...)` or an equivalent state-transition path that does not enqueue them as new events.
- `ClearDomainEvents()` is not unconditionally required when the aggregate API explicitly guarantees that reconstruction leaves the pending-event collection empty.
- If the selected constructor or replay path emits or enqueues events, or its cleanliness contract is not explicit, the mapper MUST call `ClearDomainEvents()` before returning the aggregate.
- State-based fallback reconstruction follows the same rule; constructor side effects must not escape as pending events.

---

## 🎯 Handling Value Objects

### Record Value Objects

```csharp
// Value Object definition
public sealed record ProductId(string Value)
{
    public static ProductId From(string value) => new(value);
}

// Use in a Mapper
public static ProductData ToData(Product aggregate)
{
    return new ProductData
    {
        Id = aggregate.Id.Value,  // Extract the inner value
        // ...
    };
}

public static Product ToDomain(ProductData data)
{
    var product = new Product(
        ProductId.From(data.Id),  // Rebuild the Value Object
        // ...
    );
    return product;
}
```

---

## 🎯 Error-Handling Strategy

### Graceful-Degradation Principle

```csharp
// ✅ Correct: catch and optionally log the exception without terminating
public static Product ToDomain(ProductData data)
{
    var product = new Product(...);
    
    if (!string.IsNullOrEmpty(data.DefinitionOfDoneJson))
    {
        try
        {
            var dod = JsonSerializer.Deserialize<DefinitionOfDone>(
                data.DefinitionOfDoneJson, JsonOptions);
            product.DefineDefinitionOfDone(dod);
        }
        catch (JsonException ex)
        {
            // Optional: log the error for diagnostics
            // _logger.LogWarning(ex, "Failed to deserialize DefinitionOfDone");
            
            // Degrade gracefully: continue without terminating the flow
        }
    }
    
    return product;
}

// ❌ Incorrect: allow the exception to propagate
public static Product ToDomain(ProductData data)
{
    var dod = JsonSerializer.Deserialize<DefinitionOfDone>(
        data.DefinitionOfDoneJson, JsonOptions);  // May throw
    // ...
}
```

---

### JSON Failure-Handling Rules

- A warning may be logged.
- Failure to serialize/deserialize one complex field SHOULD NOT fail the entire mapping flow.
- Critical business identity MUST NOT be silently omitted.

---

## ⚠️ Common Mistakes

### Aggregate State Is Added Without Updating Data/Mapper

**This is the easiest mistake to overlook.**

```csharp
// ❌ Incorrect: the Aggregate adds a field that the Mapper does not handle
// Product.cs
public class Product : AggregateRoot<ProductId>
{
    private readonly List<CommittedSprint> _committedSprints = new();  // New field
    
    public void CommitSprint(SprintId sprintId)
    {
        // ... business logic
    }
}

// ProductMapper.cs - ToData() was not updated ❌
// ProductMapper.cs - ToDomain() was not updated ❌
// ProductData.cs - no corresponding field ❌

// Result: after Save() and FindById(), CommittedSprints will be empty!
```

```csharp
// ✅ Correct: all three files MUST be updated together

// 1. ProductData.cs - add a field
public class ProductData
{
    public string? CommittedSprintsJson { get; set; }
}

// 2. ProductMapper.ToData() - serialize
data.CommittedSprintsJson = JsonSerializer.Serialize(
    aggregate.CommittedSprints.Select(s => s.SprintId.Value).ToList(),
    JsonOptions);

// 3. ProductMapper.ToDomain() - deserialize
if (!string.IsNullOrEmpty(data.CommittedSprintsJson))
{
    var sprintIds = JsonSerializer.Deserialize<List<string>>(
        data.CommittedSprintsJson, JsonOptions);
    foreach (var id in sprintIds ?? [])
    {
        product.CommitSprint(SprintId.From(id));
    }
}
```

---

## 🔍 Checklist

### Mapper Structure
- [ ] Uses a `static class` and `static methods`
- [ ] Handles null input (`ArgumentNullException.ThrowIfNull`)
- [ ] Configures `JsonSerializerOptions`

### ToData Method
- [ ] Maps every basic field
- [ ] Serializes complex objects as JSON
- [ ] Includes the `IsDeleted` field
- [ ] Handles serialization errors
- [ ] Includes domain events, metadata, and stream identity for a write-model mapper

### ToDomain Method
- [ ] Prefers rebuilding from events (Event Sourcing)
- [ ] Supports rebuilding from state
- [ ] Deserializes every complex object
- [ ] Restores `IsDeleted` state
- [ ] Returns the reconstructed aggregate with no pending `DomainEvents`; calls `ClearDomainEvents()` when the constructor/replay path can enqueue events or does not explicitly guarantee cleanliness
- [ ] Degrades gracefully on deserialization failure without terminating the entire flow

### ToDto Method
- [ ] Provides a Domain → DTO method
- [ ] Provides a Data → DTO method (for Projection)

---

## 📂 Code Examples

For more complete examples, see:

| Example | Path |
|------|------|
| Mapper example | [../examples/mapper/](../examples/mapper/) |
| Outbox Mapper example | [../examples/outbox/](../examples/outbox/) |
| DTO example | [../examples/dto/](../examples/dto/) |

---

## Related Documents

- [aggregate-standards.md](aggregate-standards.md)
- [repository-standards.md](repository-standards.md)
- [projection-standards.md](projection-standards.md)
- [../../guides/design-guides/FRAMEWORK-API-INTEGRATION-GUIDE.md](../../guides/design-guides/FRAMEWORK-API-INTEGRATION-GUIDE.md)
