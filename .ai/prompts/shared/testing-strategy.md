# Testing Strategy (Dotnet)

## Mandatory Decisions
- **Framework**: xUnit
- **BDD**: BDDfy fluent API with Gherkin-style naming only (no `.feature` files)
- **No BaseTestClass**: Tests must not inherit from shared base classes
- **Mocking**: NSubstitute only

## Core Rules
- Do not hardcode environment/profile inside test classes
- Use fixtures/collections to switch profiles
- Use Given/When/Then step methods or fluent chains for behavior scenarios (BDDfy)
- Verify domain events with async-safe assertions (e.g., Eventually/Retry helpers)

## Profile Switching Pattern (xUnit)
- Use `ICollectionFixture<TFixture>` to set environment variables before test execution
- Example fixture (conceptual):
  - Set `ASPNETCORE_ENVIRONMENT=test-inmemory`
  - Initialize test service container

## Test Types
- **Use Case Tests**: BDDfy scenarios with Gherkin-style names; validate command/query behavior
- **Contract Tests**: Validate preconditions (DBC) without DI
- **Controller Tests**: Integration tests using `WebApplicationFactory`
- **Reactor Tests**: Event-driven tests with async verification

## NSubstitute Rules
- Use `Substitute.For<T>()`
- Avoid strict mocks unless explicitly required


## ezSpec -> BDDfy Mapping Rules (Dotnet)

### Coverage Rules (Must Keep)
- Each Acceptance Criteria (AC) becomes at least one Scenario.
- Each AC `then`/`and` condition becomes a distinct Then/And step with explicit assertion(s).
- Maintain a checklist mapping: AC -> Scenario -> Then/And assertions (100% required).

### DSL Mapping Table
| ezSpec Concept | BDDfy Equivalent | Notes |
| --- | --- | --- |
| Feature / EzFeature | Story/test class + `[Story]` (optional) | One class per use case. |
| Scenario / EzScenario | Test method + Gherkin-style name | One scenario per AC or error case. |
| Given/When/Then/And blocks | BDDfy step methods or fluent chain | Step text mirrors spec wording. |
| ScenarioEnvironment `env.put` | Typed test context | TODO: finalize standard context pattern. |
| `env.gets(key)` / `env.get(key, Type)` | Context get with type | Prefer typed context fields over casting. |
| `.Execute()` | `this.BDDfy()` | Scenario executed in the test method. |
| Event verification (await) | Async helper in Then/And step | TODO: define `IEventProbe` + `ShouldEventuallyContain<T>()` helper. |

### Data Context Pattern (Recommended)
Use a typed context object shared by step definitions:
```csharp
public sealed class UseCaseTestContext
{
    public object? Input { get; set; }
    public object? Output { get; set; }
    public string? AggregateId { get; set; }
}
```
TODO: standardize concrete typed contexts per use case (avoid `object?` once base types are finalized).

### Example (BDDfy + Gherkin-Style Naming)
```csharp
public sealed class CreateProductUseCaseTests
{
    private readonly UseCaseTestContext _ctx = new();
    private readonly ICreateProductUseCase _useCase;
    private readonly IEventProbe _events; // TODO: implement async event probe

    public CreateProductUseCaseTests(ICreateProductUseCase useCase, IEventProbe events)
    {
        _useCase = useCase;
        _events = events;
    }

    [Fact]
    public void Create_product_successfully()
    {
        this.BDDfy();
    }

    void Given_valid_product_data()
    {
        _ctx.Input = new CreateProductInput("product-123", "Product Name", "user-1");
    }

    async Task When_I_execute_CreateProduct()
    {
        if (_ctx.Input is not CreateProductInput input) throw new InvalidOperationException("Missing input");
        _ctx.Output = await _useCase.Execute(input);
    }

    void Then_the_command_succeeds()
    {
        if (_ctx.Output is not CqrsOutput output) throw new InvalidOperationException("Missing output");
        output.ExitCode.Should().Be(ExitCode.Success);
    }

    async Task And_a_ProductCreated_event_is_published()
    {
        if (_ctx.Output is not CqrsOutput output) throw new InvalidOperationException("Missing output");
        await _events.ShouldEventuallyContain<ProductCreated>(e => e.ProductId == output.Id);
    }
}
```

### Spec Language Mapping (Position vs Order)
- "Position X" means list index `X`.
- "Order X" means entity `Order` property equals `X`.
- If spec mentions both, assert both.

```csharp
// Position check (index)
children[1].Name.Should().Be("Swimlane-0");
// Order check (property)
children[1].Order.Should().Be(1);
```

### Test vs Domain Contract Responsibilities
- Use case tests verify flow (exit code, repository state, event published).
- Domain promises (postconditions) should live in Contract/Ensure logic.
- If a spec statement looks like a domain promise, add TODO in test and suggest a domain ensure.


## Dual-Profile Execution (Dotnet)

### When `dualProfileSupport: true`
- Run **all relevant use case tests** twice: `test-inmemory` and `test-outbox`.
- Do NOT hardcode environment in test classes.
- Prefer xUnit fixtures/collections to set `ASPNETCORE_ENVIRONMENT` before host startup.

### Execution Options
1) **Two test runs (recommended in CI)**
```bash
ASPNETCORE_ENVIRONMENT=test-inmemory dotnet test
ASPNETCORE_ENVIRONMENT=test-outbox dotnet test
```

2) **Two test projects (if isolation needed)**
- `src/tests/Application.InMemory.Tests.csproj`
- `src/tests/Application.Outbox.Tests.csproj`

TODO: finalize test project naming convention for dual-profile split.

### Fixture Pattern (xUnit)
```csharp
public sealed class ProfileFixture : IDisposable
{
    private readonly string _original;

    public ProfileFixture(string environment)
    {
        _original = Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT") ?? string.Empty;
        Environment.SetEnvironmentVariable("ASPNETCORE_ENVIRONMENT", environment);
    }

    public void Dispose()
    {
        Environment.SetEnvironmentVariable("ASPNETCORE_ENVIRONMENT", _original);
    }
}

[CollectionDefinition("InMemoryProfile")]
public class InMemoryProfileCollection : ICollectionFixture<ProfileFixture> { }

// Usage:
// [Collection("InMemoryProfile")]
// public class CreateProductUseCaseTests { ... }
```

TODO: confirm environment names match `project-config.yaml` (e.g., `test-inmemory`, `test-outbox`).

### Outbox Profile Notes
- Requires PostgreSQL (message store schema).
- Ensure message table cleanup between tests if needed.

TODO: define outbox cleanup strategy for .NET (EF Core or direct SQL).
