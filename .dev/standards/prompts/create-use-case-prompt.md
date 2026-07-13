# Prompt Template: Create Use Case (Dotnet)

> Migration note:
> This file is a legacy human-facing prompt example.
> Canonical reusable prompt assets should live under `.ai/` and `.ai/assets/`.

## Input Format
```yaml
use_case_name: CreateTag
aggregate: Tag
description: Create a new tag for organizing tasks
input_fields:
  - planId: string (required)
  - name: string (required, max 50 chars)
  - color: string (required, hex color)
business_rules:
  - Tag name must be unique within a plan
  - Color must be valid hex format (#RRGGBB)
  - Plan must exist and not be deleted
```

## Expected Output

### 1) Use Case Input Model
Path: `src/Application/UseCases/<UseCase>/<UseCase>Input.cs`

```csharp
public sealed record CreateTagInput(
    string PlanId,
    string Name,
    string Color);
```

### 2) Use Case Interface and Implementation
Paths:

- `src/Application/UseCases/<UseCase>/I<UseCase>UseCase.cs`
- `src/Application/UseCases/<UseCase>/<UseCase>UseCase.cs`

```csharp
public interface ICreateTagUseCase
{
    Task<CqrsOutput> ExecuteAsync(
        CreateTagInput input,
        CancellationToken cancellationToken);
}

public sealed class CreateTagUseCase : ICreateTagUseCase
{
    private readonly IAggregateRepository<Tag, TagId> _repository;

    public CreateTagUseCase(IAggregateRepository<Tag, TagId> repository)
    {
        _repository = repository ?? throw new ArgumentNullException(nameof(repository));
    }

    public async Task<CqrsOutput> ExecuteAsync(
        CreateTagInput input,
        CancellationToken cancellationToken)
    {
        // 1. Validate input
        // 2. Load aggregate or related entities
        // 3. Execute domain logic
        // 4. Save aggregate
        // 5. Return output
        throw new NotImplementedException();
    }
}
```

### 3) Tests (xUnit + BDDfy)
Path: `src/tests/Application/<Aggregate>/UseCases/<UseCase>Tests.cs`

```csharp
// TODO: Provide BDDfy test class with Gherkin-style method names
```

## Validation Checklist
- [ ] All required fields have validation
- [ ] Business rules are enforced
- [ ] Domain events and outbound event publisher lifecycle are verified
- [ ] No direct Wolverine `IMessageBus` or other Use Case dependency exists
- [ ] Error cases are handled
- [ ] Tests cover success and failure paths
