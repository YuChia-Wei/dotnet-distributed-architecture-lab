# Testing Examples (.NET)

This folder shows how to test the .NET CA/DDD/CQRS stack with:
- xUnit for test execution
- Reqnroll (.feature) for BDD scenarios
- Wolverine for CQRS/event dispatch
- EF Core for persistence
- NSubstitute for mocks when needed

IMPORTANT:
- Do NOT use base test classes. Use fixtures and composition.
- Keep tests runnable under both InMemory and Outbox profiles.

## Structure

```
test/
├── README.md
├── TestHostFixture.cs           # DI + profile-driven test host (fixture)
├── UseCaseTestFixture.cs        # Use case helper (composition)
├── CreateTaskUseCase.feature    # Gherkin scenarios
└── CreateTaskUseCaseSteps.cs    # Step definitions (xUnit + Reqnroll)
```

## Profiles

Profile selection is external to test classes:
- InMemory: no DB, fast feedback
- Outbox: PostgreSQL + outbox, full integration

Recommended environment variables:
- `DOTNET_ENVIRONMENT=Test.InMemory`
- `DOTNET_ENVIRONMENT=Test.Outbox`

Use `TestHostFixture` to read the profile and wire the correct services.

## Contract Tests (Design by Contract)

Contract tests validate preconditions only and must be framework-light:
- Use xUnit only (no ASP.NET host or DI unless necessary)
- One command method per nested class or test group
- Assert precondition violations explicitly

```csharp
public sealed class SprintContractTests
{
    private Sprint CreateSprintWithState(SprintState state)
        => new Sprint(new SprintId("s1"), state, /* ... */);

    public sealed class StartContracts
    {
        [Fact]
        public void Start_requires_planned_state()
        {
            var sprint = CreateSprintWithState(SprintState.Started);
            Assert.Throws<PreconditionViolationException>(
                () => sprint.Start("scrum-master-1"));
        }
    }
}
```

## BDD Scenarios (Reqnroll)

Scenarios live in `.feature` files, with step definitions in `*Steps.cs`.
Use `Rule:` blocks in Gherkin to map ezSpec Rule semantics.

## Event Capture

Use a domain event collector service instead of base classes:
- InMemory: collect from in-process broker
- Outbox: collect from message store + Wolverine listeners

TODO: Implement the collector once ezDDD .NET event APIs are finalized.

## Testing Principles

- Arrange / Act / Assert (Given / When / Then)
- Tests must be isolated and order-independent
- Prefer real repositories from DI; mock only external systems
- Cover happy path, error cases, and edge cases
