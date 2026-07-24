# Shared Utility Examples

These utilities illustrate capabilities a target may implement when its
requirements and selected profiles need them. They are not mandatory shared
package APIs.

## In-Memory Infrastructure

The historical source stack supplied in-memory implementations. A .NET target
may provide project-owned implementations or select compatible packages while
preserving the same testing intent.

Illustrative components:
- InMemoryOrmDb / InMemoryOrmClient
- InMemoryMessageDb / InMemoryMessageDbClient
- InMemoryMessageBroker
- InMemoryMessageProducer

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
        // Add target-selected in-memory message store and broker when required.
        // services.AddSingleton<InMemoryMessageDb>();
        // services.AddSingleton<InMemoryMessageBroker>();

        // Example: register repository for Product
        // services.AddSingleton<IAggregateRepository<Product, ProductId>, InMemoryProductRepository>();

        return services;
    }
}
```

## Notes

- Do not reintroduce custom GenericInMemoryRepository classes.
- Resolve in-memory components from target-owned contracts and technology selections.
