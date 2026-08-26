# BDD Test Template (BDDfy + xUnit)

This template uses BDDfy and xUnit while preserving Rule-based grouping and
Given/When/Then semantics through naming and fluent steps.

## Core Rules

- Every use case must have at least one BDD scenario.
- Use Rule-prefixed test method names to group scenarios by business intent.
- Do NOT use base test classes. Use fixtures and composition.
- Resolve `testing.mocking` from target technology selections; default to NSubstitute.

## BDDfy Test Template

```csharp
public sealed class CreatePlanTests : IClassFixture<TestHostFixture>
{
    private readonly IServiceScope _scope;
    private readonly ScenarioState _state = new();

    public CreatePlanTests(TestHostFixture host)
    {
        _scope = host.Services.CreateScope();
    }

    [Fact]
    public void Rule_Successful_creation_create_plan_successfully()
    {
        this.Given(_ => Given_valid_plan_data())
            .When(_ => When_i_create_the_plan())
            .Then(_ => Then_the_plan_is_persisted())
            .BDDfy();
    }

    void Given_valid_plan_data()
    {
        _state.PlanId = Guid.NewGuid().ToString("N");
        _state.PlanName = "My Plan";
        _state.UserId = "user123";
    }

    async Task When_i_create_the_plan()
    {
        var useCase = _scope.ServiceProvider.GetRequiredService<ICreatePlanUseCase>();
        var input = new CreatePlanInput(_state.PlanId!, _state.PlanName!, _state.UserId!);
        _state.Output = await useCase.ExecuteAsync(input);
    }

    void Then_the_plan_is_persisted()
    {
        var repo = _scope.ServiceProvider.GetRequiredService<IAggregateRepository<Plan, PlanId>>();
        var saved = repo.FindByIdAsync(PlanId.ValueOf(_state.Output!.Id)).Result;
        Assert.NotNull(saved);
    }
}
```

## Rule Mapping

- A business rule maps to a `Rule_...` prefix in test method names.
- A scenario maps to a `[Fact]` test method.
- Given/When/Then maps to BDDfy fluent steps.

## Deprecated Patterns (Do NOT Use)

- TestContext singletons
- Blocking message buses
- Generic in-memory repositories
- Base test classes

## Event Capture

Use a collector service assembled through the target composition root to validate domain events.
TODO: Implement a `DomainEventCollector` integrated with Wolverine when the target selects that adapter.
