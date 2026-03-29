# Framework API Integration Guide (Dotnet)

## Key Problem Summary
1. Message store client creation is wrong
2. Outbox pattern implementation does not follow the rules
3. Import paths and annotations are misused
4. Event delivery architecture is confused (InMemory vs Outbox)

## InMemory vs Outbox Event Delivery Architecture

### InMemory Profile Event Flow
```
Repository.Save() -> InMemoryMessageStore -> InMemoryMessageBus -> Reactors
```
- Required: in-memory repository, in-memory message store, in-memory message bus
- Not required: PostgreSQL, outbox relay, durable broker
- Characteristics: synchronous, in-memory delivery, no external DB
- TODO: align exact class names when .NET ez tools are implemented

### Outbox Profile Event Flow
```
Repository.Save() -> PostgreSQL (Outbox) -> Wolverine Durable Outbox -> Message Broker -> Reactors
```
- Required: EF Core DbContext, PostgreSQL, Wolverine durable outbox, message broker
- Not required: in-memory message store
- Characteristics: async, durable, guaranteed delivery

### Key Configuration Differences
| Component | InMemory Profile | Outbox Profile |
|-----------|------------------|----------------|
| In-memory repository | Required | Not required |
| In-memory message store | Required | Not required |
| EF Core DbContext | Not required | Required |
| PostgreSQL | Not required | Required |
| Wolverine durable outbox | Not required | Required |
| Message broker | Not required | Required |
| Outbox relay/processor | Not required | Required |

## Problem 1: Message Store Client Creation

### Wrong (runtime failures)
```csharp
// Do not directly instantiate a message store client
var client = new MessageStoreClient(connectionString);
```

### Correct (DI + EF Core + Wolverine)
```csharp
// Program.cs
services.AddDbContext<AppDbContext>(options =>
    options.UseNpgsql(configuration.GetConnectionString("Outbox")));

services.AddWolverine(opts =>
{
    // TODO: confirm exact Wolverine outbox configuration for PostgreSQL
    opts.PersistMessagesWithPostgresql(configuration.GetConnectionString("Outbox"));
    opts.UseDurableOutbox();
});
```

### Why this is required
1. DI-managed lifecycle ensures correct scoping and disposal
2. Outbox needs the same transaction boundary as EF Core
3. Infrastructure needs framework-provided interceptors
4. Mapping and serialization need consistent configuration

## Problem 2: Outbox Pattern Implementation Rules (ADR-019)

### 1. OutboxMapper must be a nested class

#### Wrong: standalone class
```csharp
public class ProductOutboxMapper : IOutboxMapper<Product, ProductData>
{
    // Standalone mapper breaks the ezDDD intent
}
```

#### Correct: nested class
```csharp
public static class ProductMapper
{
    private static readonly IOutboxMapper<Product, ProductData> MapperInstance =
        new Mapper();

    public static IOutboxMapper<Product, ProductData> NewMapper() => MapperInstance;

    private sealed class Mapper : IOutboxMapper<Product, ProductData>
    {
        public Product ToDomain(ProductData data) => ProductMapper.ToDomain(data);
        public ProductData ToData(Product aggregate) => ProductMapper.ToData(aggregate);
    }
}
```

### 2. Use EF Core mapping (no JPA)

#### Wrong: Java/JPA annotations in .NET
Do not copy Java ORM annotations or imports into .NET code. Use EF Core attributes or fluent mapping instead.

#### Correct: EF Core mapping
```csharp
[Table("products")]
public class ProductData
{
    [Key]
    public string ProductId { get; set; } = string.Empty;

    [ConcurrencyCheck]
    public long Version { get; set; }
}
```

### 3. Mark outbox-only fields as NotMapped

#### Wrong: missing NotMapped
```csharp
public class ProductData
{
    public List<DomainEventData> DomainEventDatas { get; set; } = new();
    public string StreamName { get; set; } = string.Empty;
}
```

#### Correct: NotMapped for non-persistent fields
```csharp
public class ProductData
{
    [NotMapped]
    public List<DomainEventData> DomainEventDatas { get; set; } = new();

    [NotMapped]
    public string StreamName { get; set; } = string.Empty;
}
```

## Protection Checklist

### When creating the message store client
- [ ] Use DI registration (no manual instantiation)
- [ ] Use EF Core DbContext with a single connection string
- [ ] Ensure Wolverine durable outbox is enabled
- [ ] Never call `new MessageStoreClient()` directly

### When implementing OutboxMapper
- [ ] Mapper is nested in the aggregate mapper class
- [ ] Provide a static `NewMapper()` method
- [ ] Implement `ToDomain()` and `ToData()`
- [ ] Do not create a standalone mapper class

### When implementing OutboxData
- [ ] Use EF Core mapping (attributes or fluent API)
- [ ] `DomainEventDatas` is `[NotMapped]`
- [ ] `StreamName` is `[NotMapped]`
- [ ] Include concurrency/version field
- [ ] Implement `OutboxData<TId>` (TODO: define .NET interface)

## Full Example: Correct Outbox Setup

### Step 1: Data class
```csharp
[Table("products")]
public class ProductData : OutboxData<string>
{
    [NotMapped]
    public List<DomainEventData> DomainEventDatas { get; set; } = new();

    [NotMapped]
    public string StreamName { get; set; } = string.Empty;

    [Key]
    public string ProductId { get; set; } = string.Empty;

    public string Name { get; set; } = string.Empty;

    [ConcurrencyCheck]
    public long Version { get; set; }

    public bool IsDeleted { get; set; }

    public string GetId() => ProductId;
    public void SetId(string id) => ProductId = id;
}
```

### Step 2: Mapper class (nested mapper)
```csharp
public static class ProductMapper
{
    private static readonly IOutboxMapper<Product, ProductData> MapperInstance =
        new Mapper();

    public static IOutboxMapper<Product, ProductData> NewMapper() => MapperInstance;

    public static ProductData ToData(Product product)
    {
        var data = new ProductData
        {
            ProductId = product.Id.Value,
            Name = product.Name.Value,
            Version = product.Version,
            IsDeleted = product.IsDeleted
        };

        data.StreamName = product.StreamName;
        data.DomainEventDatas = product.DomainEvents
            .Select(DomainEventMapper.ToData)
            .ToList();

        return data;
    }

    public static Product ToDomain(ProductData data)
    {
        // TODO: rebuild domain object from data
        throw new NotImplementedException();
    }

    private sealed class Mapper : IOutboxMapper<Product, ProductData>
    {
        public Product ToDomain(ProductData data) => ProductMapper.ToDomain(data);
        public ProductData ToData(Product aggregate) => ProductMapper.ToData(aggregate);
    }
}
```

### Step 3: Infrastructure configuration
```csharp
// Program.cs
if (env.IsEnvironment("outbox") || env.IsEnvironment("test-outbox"))
{
    services.AddDbContext<AppDbContext>(options =>
        options.UseNpgsql(configuration.GetConnectionString("Outbox")));

    services.AddWolverine(opts =>
    {
        // TODO: confirm exact Wolverine outbox + transport config
        opts.PersistMessagesWithPostgresql(configuration.GetConnectionString("Outbox"));
        opts.UseDurableOutbox();
    });
}
```

## Common Error Diagnosis

### Error 1: No service for type 'IMessageStore'
Cause: message store client created manually or not registered
Fix: register Wolverine outbox via DI and configure persistence

### Error 2: Outbox mapper not found
Cause: mapper implemented as standalone class
Fix: move mapper into the aggregate mapper as a nested class

### Error 3: DomainEventDatas column not found
Cause: missing [NotMapped]
Fix: mark DomainEventDatas and StreamName with [NotMapped]

### Error 4: Outbox executed in InMemory profile
Cause: profile/environment not separated
Fix: ensure outbox registrations only in outbox environments

## Validation Matrix

| Component | Check | Correct Approach |
|----------|-------|------------------|
| Message store client | Creation | DI + Wolverine outbox
| OutboxMapper | Class structure | Nested class
| OutboxData | Mapping | EF Core mapping
| OutboxData | Non-persistent fields | [NotMapped]
| Configuration | Environment | outbox/test-outbox only

## Related Resources
- ADR-019: Outbox Pattern Implementation (.dev/adr/ADR-019-outbox-pattern-implementation.md)
- Outbox Sub-agent Canonical Asset (.ai/assets/sub-agent-role-prompts/outbox-sub-agent/sub-agent.yaml)
- Wolverine outbox examples (`.dev/standards/examples/outbox/README.md`, `.dev/standards/examples/aspnet-core/Program.cs`)

## Quick Checklist

```bash
# 1. Message store client instantiation
rg "new .*MessageStore" src/ && echo "Found direct instantiation"

# 2. Standalone outbox mapper
rg "class .*OutboxMapper" src/ && echo "Found standalone mapper"

# 3. NotMapped for outbox fields
rg "DomainEventDatas" src/ | rg -v "NotMapped" && echo "Missing NotMapped"

# 4. Ensure outbox config only in outbox environments
rg "UseDurableOutbox" src/ | rg -v "outbox" && echo "Check environment gating"
```




