# Shared Utilities (Required)

These utilities are required in new .NET projects.

## ezDDD .NET InMemory Infrastructure

In the legacy stack, ezDDD provides in-memory implementations.  
In .NET, these must be created or ported. Preserve the same intent.

Expected components (to be implemented in .NET):
- InMemoryOrmDb / InMemoryOrmClient
- InMemoryMessageDb / InMemoryMessageDbClient
- InMemoryMessageBroker
- InMemoryMessageProducer

TODO: Implement these in the ezDDD .NET library.

## DateProvider

Location: `src/Shared/Common/DateProvider.cs`

```csharp
namespace Shared.Common;

public static class DateProvider
{
    private static DateTimeOffset? _fixed;

    public static DateTimeOffset Now()
        => _fixed ?? DateTimeOffset.UtcNow;

    public static void UseFixed(DateTimeOffset instant)
        => _fixed = instant;

    public static void UseSystemTime()
        => _fixed = null;
}
```

## InMemory Repository Configuration (Example)

This example mirrors the legacy config pattern, but uses .NET DI.

```csharp
public static class InMemoryRepositoryConfig
{
    public static IServiceCollection AddInMemoryRepositories(
        this IServiceCollection services)
    {
        // TODO: Add in-memory message store + broker from ezDDD .NET
        // services.AddSingleton<InMemoryMessageDb>();
        // services.AddSingleton<InMemoryMessageBroker>();

        // Example: register repository for Product
        // services.AddSingleton<IRepository<Product, ProductId>, InMemoryProductRepository>();

        return services;
    }
}
```

## Notes

- Do not reintroduce custom GenericInMemoryRepository classes.
- Use the framework-provided in-memory components once available.
