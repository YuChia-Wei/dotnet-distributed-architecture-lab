# Profile-Based Testing Architecture Guide (Dotnet)

## Overview
This project uses profile-based testing to run the same tests against multiple repository implementations without rewriting test code.

**Write Once, Test Everywhere**: write tests once, run them across profiles.

```
┌───────────────────┐
│  Use Case Tests   │
│  (xUnit + BDDfy)  │
└─────────┬─────────┘
          │ uses
┌─────────▼─────────┐
│   Test Fixtures   │
└─────────┬─────────┘
          │ configures
┌─────────▼────────────────────────────────────┐
│  Environment-based DI registrations          │
├──────────────┬──────────────┬───────────────┤
│ test-inmemory│ test-outbox  │ test-esdb      │
├──────────────┼──────────────┼───────────────┤
│ InMemory     │ PostgreSQL   │ EventStore DB │
│ Repository   │ + Outbox     │ (planned)     │
└──────────────┴──────────────┴───────────────┘
```

## Supported Profiles

### 1. test-inmemory (default)
- Purpose: fast unit-style tests during development
- Characteristics: in-memory storage, no external dependencies
- Speed: fastest
- Settings: `appsettings.test-inmemory.json`

### 2. test-outbox
- Purpose: outbox integration tests
- Characteristics: real PostgreSQL, transactional verification
- Speed: medium
- Settings: `appsettings.test-outbox.json`
- Requires: PostgreSQL on localhost:5800 (per project-config.yaml)

### 3. test-esdb (planned)
- Purpose: event sourcing integration tests
- Characteristics: EventStoreDB integration
- Speed: slower
- Settings: `appsettings.test-esdb.json`

### 4. test-ezes (planned)
- Purpose: EZES event sourcing integration tests
- Characteristics: EZES database integration
- Speed: medium
- Settings: `appsettings.test-ezes.json`

## Test Authoring Guide

### Step 1: Use fixtures instead of base classes
```csharp
public sealed class CreateProductFeature : IClassFixture<TestProfileFixture>
{
    private readonly TestProfileFixture _fixture;

    public CreateProductFeature(TestProfileFixture fixture)
    {
        _fixture = fixture;
    }
}
```

### Step 2: Resolve dependencies via DI
```csharp
var useCase = _fixture.Services.GetRequiredService<ICreateProductUseCase>();
var repository = _fixture.Services.GetRequiredService<IRepository<Product, ProductId>>();
```

### Step 3: Write BDDfy tests with Gherkin-style naming
```csharp
public sealed class CreateProductFeature : IClassFixture<TestProfileFixture>
{
    private readonly TestProfileFixture _fixture;

    public CreateProductFeature(TestProfileFixture fixture)
    {
        _fixture = fixture;
    }

    [Fact]
    public void Create_product_successfully()
    {
        this.BDDfy();
    }

    void Given_valid_product_creation_input() { }

    void When_I_execute_the_create_product_use_case() { }

    void Then_the_product_is_created_successfully() { }

    void And_a_domain_event_is_emitted() { }
}
```

## Running Tests

### Option 1: dotnet test with environment
```bash
ASPNETCORE_ENVIRONMENT=test-inmemory dotnet test
ASPNETCORE_ENVIRONMENT=test-outbox dotnet test
```

### Option 2: targeted test runs
```bash
ASPNETCORE_ENVIRONMENT=test-outbox dotnet test --filter FullyQualifiedName~CreateProduct
```

### Option 3: IDE configuration
- Rider/VS: set `ASPNETCORE_ENVIRONMENT=test-outbox`
- VS Code: update `.vscode/launch.json` with env var

## Migration Notes (old -> new)

### Before (manual TestContext)
```csharp
public class CreateProductUseCaseTest
{
    private readonly TestContext _context = TestContext.Instance;

    [Fact]
    public void Test() { }
}
```

### After (fixture + DI)
```csharp
public sealed class CreateProductFeature : IClassFixture<TestProfileFixture>
{
    [Fact]
    public void Test() { }
}
```

## Coverage Strategy

```
Profile Coverage Matrix:

                 InMemory  Outbox  ESDB  EZES
Use Case Tests      ✅       ✅     🔄    🔄
Controller Tests    ✅       ✅     -     -
Integration Tests   -        ✅     ✅    ✅
E2E Tests           -        ✅     -     -
```

## Rules and Constraints

### 1. Do not hardcode repository implementations
```csharp
// Wrong
var repo = new InMemoryProductRepository();

// Correct
var repo = _fixture.Services.GetRequiredService<IRepository<Product, ProductId>>();
```

### 2. Do not set ASPNETCORE_ENVIRONMENT inside test classes
```csharp
// Wrong: hardcoded inside tests
Environment.SetEnvironmentVariable("ASPNETCORE_ENVIRONMENT", "test-inmemory");
```

### 3. Event verification
```csharp
// Use fixture-captured events or Wolverine tracking
var events = _fixture.CapturedEvents;
```

## Phase-specific Access Rules

**Given/When cannot access repositories directly; Then/And can.**

### Wrong (Given/When)
```csharp
// Given
var aggregate = new Product(...);
_repository.Save(aggregate);

// When
var product = _repository.Get(id);
product.ChangeName("new");
_repository.Save(product);
```

### Correct
```csharp
// Given: use use case
_createProductUseCase.Execute(input);

// When: use use case
_changeDescriptionUseCase.Execute(input);

// Then: read model/repository checks allowed
var product = _repository.Get(id);
product.Name.Should().Be("Updated");
```

### Access Rules Summary

| Phase | Repository Access | Direct Aggregate Calls | Notes |
|------|-------------------|------------------------|-------|
| Given | No | No | Must use use cases |
| When | No | No | Must use use cases |
| Then | Yes | Read-only | Can verify state |
| And (after Then) | Yes | Read-only | Can verify state |

## Event Clearing Timing

When you need to clear events captured during Given, **wait until events are captured** before clearing.

Wrong:
```csharp
_createProductUseCase.Execute(input);
_fixture.ClearEvents();
```

Correct:
```csharp
_createProductUseCase.Execute(input);
_fixture.AwaitEvents(count: 1);
_fixture.ClearEvents();
```

## Troubleshooting

### Problem 1: DI container fails to build
Cause: missing registration for the profile
Fix: check profile-specific registration modules

### Problem 2: Repository injection fails
Cause: the profile config did not register repository
Fix: validate `TestInMemoryConfiguration` or `TestOutboxConfiguration` modules

### Problem 3: Events not captured
Cause: fixture not used / event listeners not wired
Fix: use the shared fixture that registers event capture

### Problem 4: Outbox test profile not switching
Cause: environment set too late
Fix:
1. `ASPNETCORE_ENVIRONMENT=test-outbox dotnet test`
2. Use test runsettings or IDE env config

## Related Documents
- `.ai/prompts/testing-standards-prompt.md`
- `.ai/prompts/usecase-test-generation-prompt.md`
- `.dev/adr/ADR-021-profile-based-testing-architecture.md`

## Future Extensions
1. ESDB profile implementation
2. EZES profile implementation
3. Automated test data builders per profile
4. Performance test profile

