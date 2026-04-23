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
    private readonly IRepository<Product, ProductId> _repository;

    public CreateProductFeature(TestProfileFixture fixture)
    {
        _useCase = fixture.Services.GetRequiredService<ICreateProductUseCase>();
        _repository = fixture.Services.GetRequiredService<IRepository<Product, ProductId>>();
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
1. Tests cannot switch between profiles (test-inmemory vs test-outbox)
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

### 3. Use NSubstitute for mocks
```csharp
var messageBus = Substitute.For<IMessageBus>();
services.AddSingleton(messageBus);
```

## Migration Guide

### Step 1: Remove manual TestContext

Wrong (legacy):
```csharp
public sealed class TestContext
{
    public IRepository<Product, ProductId> Repository;
    public IMessageBus Bus;
}
```

Correct (DI + profile-based):
```csharp
var repository = _services.GetRequiredService<IRepository<Product, ProductId>>();
```

### Step 2: Use fixtures for state reset (no BaseTestClass)
```csharp
public sealed class TestProfileFixture : IAsyncLifetime
{
    public Task InitializeAsync() => Task.CompletedTask;
    public Task DisposeAsync() => Task.CompletedTask;
}
```

### Step 3: Replace @MockBean with NSubstitute DI overrides
```csharp
var bus = Substitute.For<IMessageBus>();
services.AddSingleton(bus);
```

## Test Profile Configuration

### appsettings.test-inmemory.json
```json
{
  "Data": { "DisableEfCore": true }
}
```

### appsettings.test-outbox.json
```json
{
  "ConnectionStrings": {
    "Outbox": "Host=localhost;Port=5800;Database=board_test;Username=postgres;Password=root"
  }
}
```

### Environment selection
```bash
ASPNETCORE_ENVIRONMENT=test-inmemory dotnet test
ASPNETCORE_ENVIRONMENT=test-outbox dotnet test
```

## Checklist
- [ ] Tests resolve use cases via DI (no `new`)
- [ ] No BaseTestClass or base test inheritance
- [ ] Mocking uses NSubstitute only
- [ ] Profiles switch via `ASPNETCORE_ENVIRONMENT`
- [ ] No hardcoded repository implementations in tests
- [ ] test-inmemory and test-outbox both supported

## Automated Check
Preferred active entry point:

- `.ai/scripts/check-test-di-compliance.sh`

## Common Mistakes

### 1. Hardcoding repository implementations
Wrong:
```csharp
var repo = new InMemoryProductRepository();
```

Correct:
```csharp
var repo = _services.GetRequiredService<IRepository<Product, ProductId>>();
```

### 2. Manual service construction
Wrong:
```csharp
var useCase = new CreateProductHandler(repo);
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
