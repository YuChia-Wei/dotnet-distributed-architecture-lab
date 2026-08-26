# Persistence And Messaging Integration Guide (.NET)

## Scope And Selection Boundary

This guide explains how project-owned persistence and event-publication ports
can use either in-memory adapters or a durable Outbox profile. It does not
define a required package API. EF Core, Dapper, Wolverine/WolverineFx,
PostgreSQL, and a broker are conditional .NET providers selected by the target
repository.

Code identifiers below are illustrative unless the target repository already
defines them. Do not generate a base class, interface, package reference, or
configuration call solely because it appears in this guide.

## Stable Capability Contracts

Across profiles, the Application layer depends on project-owned ports:

- an aggregate persistence port;
- an outbound event-publication port;
- optional query/projection ports;
- a target-owned unit-of-work boundary when atomic persistence is required.

The Infrastructure layer selects the concrete adapters. A Use Case must not
depend directly on an ORM, broker client, or Wolverine `IMessageBus`.

## In-Memory And Durable-Outbox Profiles

### In-Memory Flow

```text
Use Case -> Repository port -> In-memory store
         -> Event publisher port -> In-memory dispatcher -> Reactors
```

- No database, durable outbox, or external broker is required.
- Repository and publisher semantics remain compatible with the application
  ports used by the durable profile.
- Delivery and persistence are process-local and are not crash durable.

### Durable-Outbox Flow

```text
Use Case -> Repository transaction -> Aggregate state + Outbox records
         -> Durable dispatcher -> Message broker -> Consumers / Reactors
```

- Aggregate state and Outbox records must commit atomically.
- A selected provider such as Wolverine may supply durable dispatch and retry
  behavior.
- EF Core, Dapper, or direct SQL may implement persistence according to the
  target's technology selection.
- Broker and transport choices remain target-owned.

### Selection Matrix

| Capability | In-Memory Profile | Durable-Outbox Profile |
| --- | --- | --- |
| Aggregate persistence | In-memory adapter | Target-selected durable adapter |
| Event publication | In-process adapter | Durable Outbox dispatcher |
| Database / ORM | Not required | Conditional target selection |
| External broker | Not required | Conditional target selection |
| Crash durability | No | Required by the selected Outbox contract |
| Application-facing ports | Project-owned | The same project-owned contracts |

## Composition Root

Keep provider selection in explicit `IServiceCollection` composition modules.
Do not use Service Locator, DI attributes, or implicit assembly-scanning magic
as a substitute for target-owned registration.

### Illustrative In-Memory Registration

```csharp
public static IServiceCollection AddInMemoryProfile(
    this IServiceCollection services)
{
    services.AddSingleton<IAggregateRepository<Product, ProductId>,
        InMemoryProductRepository>();
    services.AddSingleton<IEventPublisher, InMemoryEventPublisher>();
    services.AddSingleton<IProductsProjection, InMemoryProductsProjection>();
    return services;
}
```

### Illustrative EF Core And Wolverine Registration

```csharp
public static IServiceCollection AddDurableOutboxProfile(
    this IServiceCollection services,
    IConfiguration configuration)
{
    var connectionString =
        configuration.GetConnectionString("Outbox")
        ?? throw new InvalidOperationException("Missing Outbox connection string.");

    services.AddDbContext<AppDbContext>(options =>
        options.UseNpgsql(connectionString));

    services.AddWolverine(options =>
    {
        // Confirm the exact API against the target-selected Wolverine version.
        options.PersistMessagesWithPostgresql(connectionString);
        options.UseDurableOutbox();
    });

    services.AddScoped<IAggregateRepository<Product, ProductId>,
        EfProductRepository>();
    return services;
}
```

The example demonstrates the composition boundary, not a guaranteed API for
every Wolverine version. A Dapper/direct-SQL adapter may satisfy the same ports
without adopting EF Core.

## Persistence Data And Mapping

Persistence DTOs may be plain classes. No shared data base class or mapper
interface is required unless the target has explicitly selected one.

```csharp
[Table("products")]
public sealed class ProductData
{
    [Key]
    [Column("product_id")]
    public string ProductId { get; set; } = string.Empty;

    [Column("name")]
    public string Name { get; set; } = string.Empty;

    [ConcurrencyCheck]
    [Column("version")]
    public long Version { get; set; }

    [NotMapped]
    public List<DomainEventData> PendingEvents { get; set; } = new();
}
```

Follow the canonical mapper standard: use explicit, symmetric conversion and
keep provider concerns outside the Domain model.

```csharp
public static class ProductMapper
{
    public static ProductData ToData(Product aggregate) => new()
    {
        ProductId = aggregate.Id.Value,
        Name = aggregate.Name.Value,
        Version = aggregate.Version,
        PendingEvents = aggregate.DomainEvents
            .Select(DomainEventMapper.ToData)
            .ToList()
    };

    public static Product ToDomain(ProductData data)
    {
        ArgumentNullException.ThrowIfNull(data);
        return Product.Rehydrate(
            new ProductId(data.ProductId),
            data.Name,
            data.Version);
    }
}
```

`Product.Rehydrate` and `DomainEventData` are project-owned examples. Use the
target's actual reconstruction and event-envelope contracts.

## Outbox Consistency Rules

- Persist aggregate state and Outbox records in one atomic transaction.
- Do not clear pending Domain Events until the selected repository contract
  confirms durable acceptance.
- Keep dispatch retry and poison-message behavior in Infrastructure.
- Make consumers idempotent according to the target's delivery guarantees.
- Do not publish directly to the broker from the Domain or Use Case layer.
- Do not execute durable adapters in the in-memory profile.

## Diagnosis

### A Use Case Resolves A Runtime Bus Directly

Move the runtime dependency to an Infrastructure adapter and inject the
project-owned event-publication port into the Use Case.

### In-Memory Startup Opens A Database Connection

EF Core or another durable adapter was registered unconditionally. Guard the
composition module with the selected profile and test each profile separately.

### Outbox Records Are Written Separately From Aggregate State

The transaction boundary is incomplete. Make the repository adapter own both
writes or use a provider integration that proves atomicity.

### Rehydration Produces New Pending Events

Use a side-effect-free reconstruction path, or clear events only when the
aggregate contract explicitly requires that cleanup after replay.

## Validation Matrix

| Surface | In-Memory Check | Durable-Outbox Check |
| --- | --- | --- |
| Composition | No ORM/broker registration | Only selected durable providers registered |
| Persistence | State round trip through in-memory adapter | Aggregate and Outbox commit atomically |
| Publication | In-process delivery reaches reactors | Durable dispatch, retry, and broker delivery verified |
| Reconstruction | No new pending events | No duplicate pending events after reload |
| Architecture | Application depends only on project ports | Runtime APIs remain in Infrastructure |

## Related Resources

- `.ai/assets/tech-stacks/dotnet-backend/standards/coding-standards.md`
- `.ai/assets/tech-stacks/dotnet-backend/standards/coding-standards/mapper-standards.md`
- `.ai/assets/tech-stacks/dotnet-backend/standards/coding-standards/repository-standards.md`
- `.ai/assets/tech-stacks/dotnet-backend/standards/USECASE-COMMAND-HANDLER-RELATIONSHIP.MD`
- `.ai/assets/tech-stacks/dotnet-backend/examples/outbox/README.md`
- `.ai/assets/tech-stacks/dotnet-backend/examples/aspnet-core/Program.cs`
- `.ai/assets/sub-agent-role-prompts/outbox-sub-agent/sub-agent.yaml`
