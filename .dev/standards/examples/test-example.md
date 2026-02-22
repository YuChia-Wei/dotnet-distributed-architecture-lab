# Testing Examples (Conceptual)

This document explains BDD testing concepts and manual setup patterns.
It is intended as learning material, not a production template.

## Intended Use

- Learn BDDfy + xUnit basics
- Understand event capture and repository wiring
- Compare InMemory vs Outbox patterns

## Core Ideas

- Use Rule-prefixed test names to express behavior
- Use DI fixtures for setup
- Avoid base test classes

## Minimal Example

```csharp
public sealed class PlanTests
{
    [Fact]
    public void Rule_Create_plan_create_a_plan_successfully()
    {
        this.Given(_ => Given_valid_input())
            .When(_ => When_i_create_the_plan())
            .Then(_ => Then_the_plan_is_saved())
            .BDDfy();
    }

    void Given_valid_input() { }
    void When_i_create_the_plan() { }
    void Then_the_plan_is_saved() { }
}
```

## Event Capture (Concept)

Use a collector service and assert against it:

```csharp
var collector = _scope.ServiceProvider.GetRequiredService<DomainEventCollector>();
Assert.Equal(1, collector.CountOf<PlanCreated>());
```

TODO: Implement the collector for Wolverine + ezDDD .NET.
