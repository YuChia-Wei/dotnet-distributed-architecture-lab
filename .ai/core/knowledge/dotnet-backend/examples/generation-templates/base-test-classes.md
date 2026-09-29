# Test Fixture Templates (No Base Classes)

These templates replace the legacy base test classes.
In .NET, use xUnit fixtures and composition (no inheritance).

## 1. TestHostFixture
Location: `tests/Infrastructure/TestHostFixture.cs`

```csharp
public sealed class TestHostFixture : IAsyncLifetime
{
    public IServiceProvider Services { get; private set; } = default!;
    public string ActiveProfile { get; } = TestProfiles.Resolve();

    public Task InitializeAsync()
    {
        var services = new ServiceCollection();

        services.AddLogging();
        // TODO: Add Wolverine + EF Core based on profile

        if (ActiveProfile == TestProfiles.InMemory)
        {
            // TODO: Add InMemory repositories + message broker
        }
        else if (ActiveProfile == TestProfiles.Outbox)
        {
            // TODO: Add PostgreSQL repositories + outbox pipeline
        }

        Services = services.BuildServiceProvider(validateScopes: true);
        return ClearStateAsync();
    }

    public Task DisposeAsync() => Task.CompletedTask;

    public Task ClearStateAsync()
    {
        // TODO: Clear stores (InMemory) or reset outbox tables
        return Task.CompletedTask;
    }
}
```

## 2. UseCaseTestFixture
Location: `tests/Infrastructure/UseCaseTestFixture.cs`

```csharp
public sealed class UseCaseTestFixture
{
    private readonly TestHostFixture _host;

    public UseCaseTestFixture(TestHostFixture host)
    {
        _host = host;
    }

    public IServiceScope CreateScope() => _host.Services.CreateScope();
}
```

## Usage Example

```csharp
public sealed class CreateProductUseCaseTests : IClassFixture<TestHostFixture>
{
    private readonly TestHostFixture _host;

    public CreateProductUseCaseTests(TestHostFixture host)
    {
        _host = host;
    }

    [Fact]
    public async Task Creates_product()
    {
        using var scope = _host.Services.CreateScope();
        // Resolve use case and repository from DI
    }
}
```

## Profile Rules

- Do NOT hardcode profile in test classes.
- Control profile using `DOTNET_ENVIRONMENT`.
- Tests must run under both InMemory and Outbox profiles.
