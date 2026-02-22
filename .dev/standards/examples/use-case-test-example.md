# Use Case Test Example (.NET)

## Overview
This example shows a modern testing pattern using:
- BDDfy (Gherkin-style naming)
- xUnit
- DI fixtures (no base test classes)
- Wolverine + EF Core

## Core Rules

1. Profile-based testing (InMemory vs Outbox)
2. No base test classes
3. Aggregate IDs use GUIDs
4. Command tests must verify events

## Example: Create Sprint (Command)

```csharp
public sealed class CreateSprintTests
{
    private readonly IServiceScope _scope;
    private readonly ScenarioState _state = new();

    public CreateSprintTests(TestHostFixture host)
    {
        _scope = host.Services.CreateScope();
    }

    [Fact]
    public void Rule_Successful_creation_create_sprint_successfully()
    {
        this.Given(_ => Given_valid_sprint_input())
            .When(_ => When_i_create_the_sprint())
            .Then(_ => Then_the_sprint_is_persisted())
            .And(_ => And_a_SprintCreated_event_is_published())
            .BDDfy();
    }

    void Given_valid_sprint_input()
    {
        _state.ProductId = Guid.NewGuid().ToString("N");
        _state.SprintId = Guid.NewGuid().ToString("N");
        _state.CreatorId = "test-creator";
        _state.Name = "Sprint 1";
    }

    async Task When_i_create_the_sprint()
    {
        var useCase = _scope.ServiceProvider.GetRequiredService<ICreateSprintUseCase>();
        var input = new CreateSprintInput(
            _state.ProductId!, _state.SprintId!, _state.Name!, _state.CreatorId!);
        _state.Output = await useCase.ExecuteAsync(input);
    }

    async Task Then_the_sprint_is_persisted()
    {
        var repo = _scope.ServiceProvider.GetRequiredService<IRepository<Sprint, SprintId>>();
        var saved = await repo.FindByIdAsync(SprintId.ValueOf(_state.Output!.Id));
        Assert.NotNull(saved);
    }

    void And_a_SprintCreated_event_is_published()
    {
        var collector = _scope.ServiceProvider.GetRequiredService<DomainEventCollector>();
        Assert.Equal(1, collector.CountOf<SprintCreated>());
    }
}
```

## Event Verification (Mandatory)

Command tests must verify events using a collector service:
```csharp
var collector = _scope.ServiceProvider.GetRequiredService<DomainEventCollector>();
Assert.Equal(1, collector.CountOf<SprintCreated>());
```

TODO: Implement `DomainEventCollector` using Wolverine + ezDDD .NET.

## Error Handling Pattern

```csharp
try
{
    await useCase.ExecuteAsync(input);
}
catch (Exception ex)
{
    Assert.Contains("name", ex.Message);
}
```
