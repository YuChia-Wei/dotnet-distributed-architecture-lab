# Profile Configuration Complexity Solution (Dotnet)

## Problem Summary
Profile configuration complexity introduces three major challenges:
1. Conditional DI registration for different profiles
2. ORM configuration conflicts (InMemory should not initialize EF Core)
3. Dependency graph complexity for outbox mode

## Profile Architecture and Isolation Strategy

```
Profile isolation
├── Configuration isolation
│   ├── InMemoryConfiguration (inmemory only)
│   ├── OutboxConfiguration (outbox only)
│   └── CommonConfiguration (shared)
│
├── Settings isolation
│   ├── appsettings.json
│   ├── appsettings.inmemory.json
│   ├── appsettings.outbox.json
│   ├── appsettings.test-inmemory.json
│   └── appsettings.test-outbox.json
│
└── Service isolation
    ├── Repository registrations (profile-specific)
    ├── DbContext registrations (outbox only)
    └── Use case handlers (profile-independent)
```

## Solution 1: Conditional DI Registration

### Strategy: profile-specific configuration modules

```csharp
// Common registrations
public static class CommonConfiguration
{
    public static IServiceCollection AddUseCases(this IServiceCollection services)
    {
        services.AddScoped<ICreateProductUseCase, CreateProductHandler>();
        services.AddScoped<IGetProductsUseCase, GetProductsHandler>();
        return services;
    }
}

// InMemory registrations
public static class InMemoryConfiguration
{
    public static IServiceCollection AddInMemoryProfile(this IServiceCollection services)
    {
        // TODO: replace with .NET ez in-memory store classes when available
        services.AddSingleton<IMessageStore, InMemoryMessageStore>();
        services.AddSingleton<IMessageBus, InMemoryMessageBus>();
        services.AddSingleton<IRepository<Product, ProductId>, InMemoryProductRepository>();
        services.AddSingleton<IProductsProjection, InMemoryProductsProjection>();
        return services;
    }
}

// Outbox registrations
public static class OutboxConfiguration
{
    public static IServiceCollection AddOutboxProfile(this IServiceCollection services, IConfiguration config)
    {
        services.AddDbContext<AppDbContext>(o =>
            o.UseNpgsql(config.GetConnectionString("Outbox")));

        services.AddWolverine(opts =>
        {
            // TODO: confirm exact Wolverine outbox config
            opts.PersistMessagesWithPostgresql(config.GetConnectionString("Outbox"));
            opts.UseDurableOutbox();
        });

        services.AddScoped<IRepository<Product, ProductId>, OutboxProductRepository>();
        services.AddScoped<IProductsProjection, EfProductsProjection>();
        return services;
    }
}
```

## Solution 2: ORM Configuration Conflicts

### Strategy: environment-specific appsettings and guarded registrations

```json
// appsettings.inmemory.json
{
  "Data": {
    "DisableEfCore": true
  }
}

// appsettings.outbox.json
{
  "ConnectionStrings": {
    "Outbox": "Host=localhost;Port=5432;Database=aiscrum;Username=postgres;Password=root"
  }
}
```

```csharp
if (!config.GetValue<bool>("Data:DisableEfCore"))
{
    services.AddDbContext<AppDbContext>(o =>
        o.UseNpgsql(config.GetConnectionString("Outbox")));
}
```

## Solution 3: Dependency Graph Complexity

### Strategy: layered registration order

```csharp
// Layer 1: infrastructure
public static class OutboxInfrastructureConfiguration
{
    public static IServiceCollection AddOutboxInfrastructure(this IServiceCollection services, IConfiguration config)
    {
        services.AddDbContext<AppDbContext>(o =>
            o.UseNpgsql(config.GetConnectionString("Outbox")));
        return services;
    }
}

// Layer 2: outbox
public static class OutboxOrmConfiguration
{
    public static IServiceCollection AddOutboxOrm(this IServiceCollection services, IConfiguration config)
    {
        services.AddWolverine(opts =>
        {
            opts.PersistMessagesWithPostgresql(config.GetConnectionString("Outbox"));
            opts.UseDurableOutbox();
        });
        return services;
    }
}

// Layer 3: repositories
public static class OutboxRepositoryConfiguration
{
    public static IServiceCollection AddOutboxRepositories(this IServiceCollection services)
    {
        services.AddScoped<IRepository<Product, ProductId>, OutboxProductRepository>();
        return services;
    }
}
```

## Profile Conflict Diagnostics

### Diagnostic Script (TODO)
Create a `.sh` script to scan for environment gating and check that:
- InMemory profile has no EF Core registration
- Outbox profile has EF Core + Wolverine outbox registration
- Repositories are registered per profile

## Profile Decision Matrix (ezapp 2.0.0 intent)

| Profile | DbContext | EF Core | Repository Type | Message Bus | Projection Type |
|---------|-----------|---------|-----------------|-------------|-----------------|
| inmemory | ❌ | ❌ | InMemoryRepository | InMemoryMessageBus | InMemoryProjection |
| outbox | ✅ | ✅ | OutboxRepository | DurableMessageBus | EfProjection |
| test-inmemory | ❌ | ❌ | InMemoryRepository | InMemoryMessageBus | InMemoryProjection |
| test-outbox | ✅ | ✅ | OutboxRepository | DurableMessageBus | EfProjection |

> ezapp 2.0.0 intent: InMemory and Outbox profiles both use OutboxRepository semantics; they differ in the storage and message transport implementations.

## Best Practices

### 1. Configuration organization
```
config/
├── common/
│   └── CommonConfiguration.cs
├── inmemory/
│   └── InMemoryConfiguration.cs
└── outbox/
    ├── OutboxInfrastructureConfiguration.cs
    ├── OutboxOrmConfiguration.cs
    └── OutboxRepositoryConfiguration.cs
```

### 2. Profile enable rules
```csharp
if (env.IsEnvironment("inmemory") || env.IsEnvironment("test-inmemory"))
{
    services.AddInMemoryProfile();
}

if (env.IsEnvironment("outbox") || env.IsEnvironment("test-outbox"))
{
    services.AddOutboxProfile(config);
}
```

### 3. Test profile isolation
```csharp
// InMemory tests
// TODO: use xUnit fixtures + BDDfy (Gherkin-style naming); no BaseTestClass

// Outbox tests
// TODO: use xUnit fixtures + BDDfy (Gherkin-style naming); no BaseTestClass
```

## Common Pitfalls and Fixes

Pitfall 1: Profile inheritance in config
```bash
# Wrong
ASPNETCORE_ENVIRONMENT=test,test-inmemory

# Correct
ASPNETCORE_ENVIRONMENT=test-inmemory
```

Pitfall 2: DI registration conflicts
```csharp
// Wrong: conflicting registrations with different service types
services.AddSingleton<IRepository, InMemoryRepository>();
services.AddSingleton<IRepository, OutboxRepository>();

// Correct: register the same service type per profile only
```

Pitfall 3: InMemory config accidentally depends on EF Core
```csharp
// Wrong
services.AddDbContext<AppDbContext>();

// Correct
// Only add DbContext in outbox environments
```

## Quick Checklist

### InMemory profile
- [ ] No EF Core registrations
- [ ] Dedicated InMemory configuration module
- [ ] No DbContext or Npgsql usage
- [ ] InMemory message store and message bus are registered
- [ ] Repository uses in-memory storage

### Outbox profile
- [ ] EF Core DbContext registered
- [ ] Wolverine durable outbox enabled
- [ ] Outbox repository registered
- [ ] EF Core + outbox config separated from InMemory profile
- [ ] No in-memory message bus in outbox

This solution reduces profile conflicts and keeps the DI graph predictable for both InMemory and Outbox modes.


