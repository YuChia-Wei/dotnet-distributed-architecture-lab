# New Project Test Setup Guide (Dotnet)

## Purpose
Set up the testing infrastructure for a new .NET project to support multi-profile testing (test-inmemory and test-outbox).

## Prerequisites
1. .NET SDK installed (version defined in `.dev/project-config.yaml`)
2. WolverineFx and EF Core packages available
3. A shared time provider (DateProvider/TimeProvider) is defined for deterministic tests

## Setup Steps

### Step 1: Create test fixtures (no base test class)

Create a shared fixture to host DI and event capture.

Path: `src/tests/Shared/TestProfileFixture.cs`

```csharp
public sealed class TestProfileFixture : IAsyncLifetime
{
    public IServiceProvider Services { get; private set; } = default!;
    private readonly FakeEventListener _eventListener = new();

    public Task InitializeAsync()
    {
        var services = new ServiceCollection();

        // TODO: load ASPNETCORE_ENVIRONMENT and choose profile registrations
        services.AddUseCases();
        services.AddInMemoryProfile();

        services.AddSingleton(_eventListener);
        Services = services.BuildServiceProvider();
        return Task.CompletedTask;
    }

    public Task DisposeAsync() => Task.CompletedTask;

    public Task AwaitEvents(int count)
    {
        // TODO: async-safe wait for event capture
        return Task.CompletedTask;
    }

    public void ClearEvents() => _eventListener.Clear();
}
```

### Step 2: Add profile-specific registrations

Create test registration modules (no BaseTestClass).

Example path: `src/tests/Profiles/TestProfileRegistration.cs`

```csharp
public static class TestProfileRegistration
{
    public static IServiceCollection AddTestProfiles(this IServiceCollection services, IConfiguration config)
    {
        var environment = config["ASPNETCORE_ENVIRONMENT"] ?? "test-inmemory";

        if (environment == "test-inmemory")
        {
            services.AddInMemoryProfile();
        }

        if (environment == "test-outbox")
        {
            services.AddOutboxProfile(config);
        }

        return services;
    }
}
```

### Step 3: Configure test settings

`appsettings.test-inmemory.json`
```json
{
  "Data": { "DisableEfCore": true }
}
```

`appsettings.test-outbox.json`
```json
{
  "ConnectionStrings": {
    "Outbox": "Host=localhost;Port=5800;Database=board_test;Username=postgres;Password=root"
  }
}
```

### Step 4: Optional test grouping

Use xUnit traits and `dotnet test --filter` instead of JUnit suites.

```csharp
[Trait("Profile", "test-inmemory")]
public sealed class CreateProductFeature : IClassFixture<TestProfileFixture> { }
```

```bash
ASPNETCORE_ENVIRONMENT=test-inmemory dotnet test --filter Profile=test-inmemory
ASPNETCORE_ENVIRONMENT=test-outbox dotnet test --filter Profile=test-outbox
```

## Writing Tests

Example BDDfy test skeleton (Gherkin-style naming, no `.feature`):

```csharp
public sealed class CreateProductFeature : IClassFixture<TestProfileFixture>
{
    private readonly ICreateProductUseCase _useCase;

    public CreateProductFeature(TestProfileFixture fixture)
    {
        _useCase = fixture.Services.GetRequiredService<ICreateProductUseCase>();
    }

    [Fact]
    public void Create_product_successfully()
    {
        this.BDDfy();
    }

    void Given_a_valid_create_product_request()
    {
        // TODO: prepare input
    }

    async Task When_the_use_case_is_executed()
    {
        await _useCase.Execute(CreateProductInput.Create("product-123", "AI Scrum Assistant", "user-456"));
    }

    void Then_the_command_succeeds()
    {
        // TODO: assert output and events
    }
}
```

## Common Pitfalls to Avoid

Do not:
1. Create BaseTestClass/BaseUseCaseTest
2. Hardcode repository implementations in tests
3. Set ASPNETCORE_ENVIRONMENT inside test classes
4. Use Thread.Sleep instead of async waits
5. Mix test and production registrations

Do:
1. Use fixtures for DI setup
2. Use NSubstitute for mocks
3. Keep profile registrations isolated
4. Clear events between scenarios
5. Use `dotnet test` with environment variables

## Verification Checklist
- [ ] No BaseTestClass or base test inheritance
- [ ] Event capture mechanism implemented
- [ ] Profile-specific registrations exist
- [ ] Test settings files present
- [ ] All tests resolve dependencies via DI
- [ ] Tests use async-safe event checks

## Related Documents
- `.dev/guides/PROFILE-BASED-TESTING-GUIDE.md`
- `.ai/assets/sub-agent-role-prompts/usecase-test-sub-agent/sub-agent.yaml`
- `.ai/assets/shared/testing-standards.md`


