# AI Prompt for Test Case Generation (.NET)

## Context
Generate use case tests that follow:
- xUnit
- BDDfy (Gherkin-style naming)
- Fixture-based DI (no base test classes)
- Wolverine for CQRS messaging
- EF Core for persistence

## Recommended Pattern (Fixture + BDDfy)

```csharp
public sealed class CreateAggregateTests
{
    private readonly IServiceScope _scope;

    public CreateAggregateTests(TestHostFixture host)
    {
        _scope = host.Services.CreateScope();
    }

    [Fact]
    public void Rule_Happy_path_create_succeeds()
    {
        this.Given(_ => Given_valid_input())
            .When(_ => When_i_execute_the_use_case())
            .Then(_ => Then_the_aggregate_is_persisted())
            .BDDfy();
    }

    void Given_valid_input() { }

    async Task When_i_execute_the_use_case()
    {
        var useCase = _scope.ServiceProvider.GetRequiredService<ICreateAggregateUseCase>();
        await useCase.ExecuteAsync(/* input */);
    }

    void Then_the_aggregate_is_persisted() { }
}
```

## Event Verification

Use a collector service for domain events:
```csharp
var collector = _scope.ServiceProvider.GetRequiredService<DomainEventCollector>();
Assert.Equal(1, collector.CountOf<AggregateCreated>());
```

TODO: Implement the collector with Wolverine integration.

## Deprecated Patterns (Do NOT Use)

- Manual TestContext singletons
- Custom GenericInMemoryRepository
- BlockingMessageBus
- Base test classes

TODO: Legacy names from the source stack are kept for context only; do not reintroduce them.

## Checklist

- [ ] Use fixture-based DI
- [ ] Use BDDfy scenarios with Gherkin-style naming
- [ ] Verify persistence and events
- [ ] Support both InMemory and Outbox profiles
