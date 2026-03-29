# Data Class Standards Guide (Dotnet)

## Overview
Data classes in the ezDDD framework serve as DTOs for persisting aggregate state in the Outbox pattern. In .NET, they are EF Core entities that represent the database schema and the outbox payload shape.

## Critical Rules

### 1. No enum fields in data classes
Data classes must not use enum-typed properties. Persist the string value instead.

Wrong:
```csharp
public ProductLifecycleState State { get; set; }
```

Correct:
```csharp
public string State { get; set; } = string.Empty;
```

### 2. No automatic enum-to-string mapping in data classes
Keep data classes string-only and perform conversion in the mapper layer.

Mapper conversion:
```csharp
// ToData
data.State = aggregate.State.ToString();

// ToDomain
var state = Enum.Parse<ProductLifecycleState>(data.State);
```

## Data Class Structure

### Basic Template
```csharp
[Table("products")]
public class ProductData : OutboxData<string>
{
    [NotMapped]
    public List<DomainEventData> DomainEventDatas { get; set; } = new();

    [NotMapped]
    public string StreamName { get; set; } = string.Empty;

    [Key]
    [Column("product_id")]
    public string ProductId { get; set; } = string.Empty;

    [Column("name")]
    public string Name { get; set; } = string.Empty;

    [Column("state")]
    public string State { get; set; } = string.Empty;

    [Column("is_deleted")]
    public bool IsDeleted { get; set; }

    [ConcurrencyCheck]
    [Column("version")]
    public long Version { get; set; }

    public string GetId() => ProductId;
    public void SetId(string id) => ProductId = id;
}
```

## Type Conversion Rules

### Enum to string
```csharp
// Mapper.ToData
data.State = aggregate.State.ToString();

// Mapper.ToDomain
var state = Enum.Parse<ProductLifecycleState>(data.State);
```

### Complex value objects to JSON
```csharp
[Column("metadata")]
public string Metadata { get; set; } = "{}";

// Mapper
data.Metadata = JsonSerializer.Serialize(aggregate.Metadata, JsonOptions.Default);
aggregate.Metadata = JsonSerializer.Deserialize<Metadata>(data.Metadata, JsonOptions.Default);
```

### Collections to JSON
```csharp
[Column("tags")]
public string Tags { get; set; } = "[]";

// Mapper
data.Tags = JsonSerializer.Serialize(aggregate.Tags, JsonOptions.Default);
aggregate.Tags = JsonSerializer.Deserialize<List<Tag>>(data.Tags, JsonOptions.Default) ?? new();
```

## EF Core Mapping Guidelines

### Required mapping signals
- Use either attributes or fluent configuration, but be explicit about column names.
- Use snake_case for database columns.
- Mark outbox-only fields with [NotMapped].
- Use a concurrency token (Version) for optimistic locking.

Fluent mapping example:
```csharp
modelBuilder.Entity<ProductData>(builder =>
{
    builder.ToTable("products");
    builder.HasKey(x => x.ProductId);
    builder.Property(x => x.ProductId).HasColumnName("product_id");
    builder.Property(x => x.Name).HasColumnName("name").IsRequired();
    builder.Property(x => x.State).HasColumnName("state").IsRequired();
    builder.Property(x => x.IsDeleted).HasColumnName("is_deleted");
    builder.Property(x => x.Version).HasColumnName("version").IsConcurrencyToken();
    builder.Ignore(x => x.DomainEventDatas);
    builder.Ignore(x => x.StreamName);
});
```

## Common Mistakes

Mistake 1: Using enum-typed properties in data classes
```csharp
public ProductLifecycleState State { get; set; }
```

Mistake 2: Missing [NotMapped] for outbox-only fields
```csharp
public List<DomainEventData> DomainEventDatas { get; set; }
```

Mistake 3: Relying on implicit EF Core mapping
```csharp
public string ProductName { get; set; }
```

## Validation Checklist

Before committing a data class:
- [ ] No enum-typed fields (all enums stored as string)
- [ ] All persistent fields mapped with explicit column names
- [ ] Outbox-only fields marked [NotMapped]
- [ ] Concurrency/version field present
- [ ] Implements OutboxData<string> (TODO: define .NET interface)
- [ ] Table and key mapping defined
- [ ] Column names use snake_case

## Validation Script

TODO: create a .NET equivalent of `.ai/scripts/check-data-class-annotations.sh`.

## Related Documents
- `FRAMEWORK-API-INTEGRATION-GUIDE.md`
- `.ai/assets/shared/dto-conventions.md`
- `.dev/standards/examples/dto/README.md`




