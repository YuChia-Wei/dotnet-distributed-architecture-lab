# Use Case Injection (DI) for .NET

## Overview
Use case wiring is done via .NET DI registration, not a central framework class.
Keep configuration organized by profile and aggregate.

## Key Principles

1. **Profile-based repository selection**  
   - InMemory for fast tests  
   - Outbox (PostgreSQL) for integration
2. **Constructor injection** for all services
3. **Single source of wiring** using extension methods

## Recommended Structure

```
src/
  Infrastructure/
    DependencyInjection.cs
    InMemoryRepositoryConfig.cs
    OutboxRepositoryConfig.cs
  UseCases/
    UseCaseConfiguration.cs
```

## Example: DependencyInjection.cs

```csharp
public static class DependencyInjection
{
    public static IServiceCollection AddUseCases(
        this IServiceCollection services)
    {
        services.AddScoped<ICreatePlanUseCase, CreatePlanService>();
        services.AddScoped<ICreateTaskUseCase, CreateTaskService>();
        return services;
    }
}
```

## Example: Profile-Based Repository Wiring

```csharp
public static IServiceCollection AddRepositories(
    this IServiceCollection services,
    string profile)
{
    if (profile == TestProfiles.InMemory)
    {
        services.AddInMemoryRepositories();
    }
    else if (profile == TestProfiles.Outbox)
    {
        services.AddOutboxRepositories();
    }

    return services;
}
```

## Adding a New Aggregate

1. Add repository registration in InMemory and Outbox configs.
2. Register use case services in `AddUseCases`.
3. Add projection registrations if needed.

## Common Mistakes

- Wiring repositories without profile guards
- Mixing InMemory + Outbox registrations in the same profile
- Registering controllers/use cases in multiple places

## Checklist

- [ ] Profile decides repository implementation
- [ ] Use case services are registered once
- [ ] All dependencies use constructor injection
