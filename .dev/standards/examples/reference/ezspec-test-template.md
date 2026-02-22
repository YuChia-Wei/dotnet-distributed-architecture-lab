# BDD Test Template (BDDfy + xUnit)

This template replaces ezSpec usage with BDDfy and xUnit.
It preserves Rule-based grouping and Given/When/Then semantics via naming and fluent steps.

## Core Rules

- Every use case must have at least one BDD scenario.
- Use Rule-prefixed test method names to group scenarios by business intent.
- Do NOT use base test classes. Use fixtures and composition.
- Use NSubstitute for mocks.

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
        var repo = _scope.ServiceProvider.GetRequiredService<IRepository<Plan, PlanId>>();
        var saved = repo.FindByIdAsync(PlanId.ValueOf(_state.Output!.Id)).Result;
        Assert.NotNull(saved);
    }
}
```

## Rule Mapping (ezSpec -> BDDfy)

- `feature.NewRule("...")` -> `Rule_...` prefix in test method names
- `@EzScenario` -> `[Fact]` test method
- `Given/When/Then` -> BDDfy steps (`Given/When/Then` fluent chain)

## Deprecated Patterns (Do NOT Use)

- TestContext singletons
- BlockingMessageBus
- GenericInMemoryRepository
- Base test classes

TODO: Legacy names from the source stack are kept for context only; do not reintroduce them.

## Event Capture

Use a collector service (composition) to validate domain events.
TODO: Implement a `DomainEventCollector` integrated with Wolverine.
