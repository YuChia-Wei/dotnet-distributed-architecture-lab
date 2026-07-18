# Dependency Injection Testing Guide (.NET)

> Active .NET practice in this repository is xUnit fixture-based testing plus `IServiceCollection` registration.

## Framework Intent To Preserve

### Deprecated legacy patterns
- Do not use manual in-memory repositories or blocking message buses.
- Replace manual wiring with DI + profile-based registrations.

### Recommended approach
```csharp
// Use DI to resolve dependencies
public sealed class CreateProductFeature : IClassFixture<TestProfileFixture>
{
    private readonly ICreateProductUseCase _useCase;
    private readonly IAggregateRepository<Product, ProductId> _repository;

    public CreateProductFeature(TestProfileFixture fixture)
    {
        _useCase = fixture.Services.GetRequiredService<ICreateProductUseCase>();
        _repository = fixture.Services.GetRequiredService<IAggregateRepository<Product, ProductId>>();
    }
}
```

### Framework-provided InMemory classes (concepts to preserve)
The original framework lineage included the following concepts. .NET equivalents should preserve the same intent:
- InMemoryOrmDb
- InMemoryOrmClient
- InMemoryMessageDb
- InMemoryMessageDbClient
- InMemoryMessageBroker
- InMemoryMessageProducer

TODO: define .NET implementations that mirror these concepts.

## Problem Background

Many tests still create objects with `new` instead of using DI. This causes:
1. Tests cannot switch between profiles (`TestInMemory` vs `TestOutbox`)
2. Tests diverge from runtime behavior
3. Loss of framework-level test features (transactional behavior, DI validation, mock registration)
4. Legacy manual wiring leaks into modern tests

## Correct Test Architecture

### 1. Use xUnit fixtures instead of base classes
```csharp
public sealed class CreateProductFeature : IClassFixture<TestProfileFixture>
{
    private readonly IServiceProvider _services;

    public CreateProductFeature(TestProfileFixture fixture)
    {
        _services = fixture.Services;
    }
}
```

### 2. Register test-specific services via DI
```csharp
// TestProfileFixture
public sealed class TestProfileFixture
{
    public IServiceProvider Services { get; }

    public TestProfileFixture()
    {
        var services = new ServiceCollection();

        // TODO: add profile selection based on ASPNETCORE_ENVIRONMENT
        services.AddUseCases();
        services.AddInMemoryProfile();

        Services = services.BuildServiceProvider();
    }
}
```

### 3. Resolve the target mocking selection

Resolve `.dev/project-config.yaml#technologySelections` slot
`testing.mocking`. Use NSubstitute when the slot is absent because it is the
dotnet-backend profile default; use the recorded target selection otherwise.

```csharp
// NSubstitute default-profile example
var eventPublisher = Substitute.For<IProductEventPublisher>();
services.AddSingleton(eventPublisher);
```

## Migration Guide

### Step 1: Remove manual TestContext

Wrong (legacy):
```csharp
public sealed class TestContext
{
    public IAggregateRepository<Product, ProductId> Repository;
    public IProductEventPublisher EventPublisher;
}
```

Correct (DI + profile-based):
```csharp
var repository = _services.GetRequiredService<IAggregateRepository<Product, ProductId>>();
```

### Step 2: Use fixtures for state reset (no BaseTestClass)
```csharp
public sealed class TestProfileFixture : IAsyncLifetime
{
    public Task InitializeAsync() => Task.CompletedTask;
    public Task DisposeAsync() => Task.CompletedTask;
}
```

### Step 3: Replace @MockBean with target-selected DI test doubles

The following snippet shows the NSubstitute default:

```csharp
var eventPublisher = Substitute.For<IProductEventPublisher>();
services.AddSingleton(eventPublisher);
```

## Test Profile Configuration

### appsettings.TestInMemory.json
```json
{
  "Data": { "DisableEfCore": true }
}
```

### appsettings.TestOutbox.json
```json
{
  "ConnectionStrings": {
    "Outbox": "Host=${DB_HOST};Port=${DB_PORT};Database=${DB_NAME};Username=${DB_USER};Password=${DB_PASSWORD}"
  }
}
```

### Environment selection
```bash
ASPNETCORE_ENVIRONMENT=TestInMemory dotnet test
ASPNETCORE_ENVIRONMENT=TestOutbox dotnet test
```

## Checklist
- [ ] Tests resolve use cases via DI (no `new`)
- [ ] No BaseTestClass or base test inheritance
- [ ] Mocking uses the resolved `testing.mocking` selection; NSubstitute is the default
- [ ] Profiles switch via `ASPNETCORE_ENVIRONMENT`
- [ ] No hardcoded repository implementations in tests
- [ ] `TestInMemory` and `TestOutbox` are both supported when the target adopts both profiles

## Automated Check
Preferred active entry point:

- `.ai/scripts/check-test-di-compliance.sh` is a transitional helper. Prefer analyzer or test architecture rules after dotnet-native validation exists.

## Common Mistakes

### 1. Hardcoding repository implementations
Wrong:
```csharp
var repo = new InMemoryProductRepository();
```

Correct:
```csharp
var repo = _services.GetRequiredService<IAggregateRepository<Product, ProductId>>();
```

### 2. Manual service construction
Wrong:
```csharp
var useCase = new CreateProductUseCase(repo, eventPublisher);
```

Correct:
```csharp
var useCase = _services.GetRequiredService<ICreateProductUseCase>();
```

### 3. Ignoring profile differences
Wrong:
```csharp
var projection = new InMemoryProductsProjection();
```

Correct:
```csharp
var projection = _services.GetRequiredService<IProductsProjection>();
```
