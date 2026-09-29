# Test Suite Templates (xUnit + Filters)

.NET does not use suite classes. Use traits and filters instead.

## Rule: Do Not Manually List Test Classes

Avoid hard-coded lists. Use naming + traits to select tests.

## InMemory Test Suite (Filter-Based)

Mark tests:
```csharp
[Trait("Category", "InMemory")]
public sealed class CreatePlanUseCaseTests { }
```

Run:
```bash
DOTNET_ENVIRONMENT=Test.InMemory dotnet test --filter "Category=InMemory"
```

## Outbox Test Suite (Filter-Based)

Mark tests:
```csharp
[Trait("Category", "Outbox")]
public sealed class ProductOutboxRepositoryTests { }
```

Run:
```bash
DOTNET_ENVIRONMENT=Test.Outbox dotnet test --filter "Category=Outbox"
```

## Use Case Only Suite

```bash
dotnet test --filter "Category=UseCase"
```

## Profile Precedence

1. `DOTNET_ENVIRONMENT`
2. Test host fixture configuration

## Checklist

- [ ] Use traits to group tests
- [ ] Use filters in CI (no manual lists)
- [ ] Keep tests profile-agnostic
