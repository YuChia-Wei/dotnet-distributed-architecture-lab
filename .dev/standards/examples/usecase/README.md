# Use Case Patterns (.NET)

This folder shows Use Case patterns aligned with Clean Architecture.

## Overview

Use Cases are the application layer. Each Use Case:
- Encapsulates one business action
- Orchestrates Domain + Infrastructure
- Is framework-agnostic in its core logic

## ezapp 2.x Concepts (Preserved)

Legacy (ezapp 1.x) patterns to avoid:
- `GenericInMemoryRepository` (replaced by Outbox + InMemory ORM)
- `BlockingMessageBus` (replaced by InMemory message broker)

.NET equivalents are **TODO** until ezDDD/ezapp ports exist. Keep the architecture intent:
- Profile-based wiring (`test-inmemory` vs `test-outbox`)
- Repository + Outbox with Wolverine + EF Core
- In-memory implementations for fast tests

## CQRS Command vs Query

### Command
Modifies state; returns `CqrsOutput`:

```csharp
public sealed class CreateTaskService : ICreateTaskUseCase
{
    public CqrsOutput Execute(CreateTaskInput input) { /* ... */ }

    // Wolverine handler entry point
    public CqrsOutput Handle(CreateTaskInput input) => Execute(input);
}
```

### Query
Reads data; returns DTOs or a typed output:

```csharp
public sealed class GetPlansService : IGetPlansUseCase
{
    public GetPlansOutput Execute(GetPlansInput input) { /* ... */ }
    public GetPlansOutput Handle(GetPlansInput input) => Execute(input);
}
```

## Structure

```
usecase/
├── README.md
├── CreatePlanUseCase.cs / CreatePlanService.cs
├── CreateTaskUseCase.cs / CreateTaskService.cs
├── DeleteTaskUseCase.cs / DeleteTaskService.cs
├── RenameTaskUseCase.cs / RenameTaskService.cs
├── AssignTagUseCase.cs / AssignTagService.cs
├── GetPlanUseCase.cs / GetPlanService.cs
├── GetPlansUseCase.cs / GetPlansService.cs
├── GetTasksByDateUseCase.cs / GetTasksByDateService.cs
└── UseCaseContracts.cs
```

## Key Principles

1. **Single Responsibility**  
   One Use Case = one business action.
2. **Dependency Inversion**  
   Depend on repository/projection abstractions.
3. **Error Handling**  
   Use `CqrsOutput` with clear failure messages.
4. **Transactional Boundary**  
   One Use Case = one transaction boundary.

## Testing Notes

- Use xUnit + BDDfy (Gherkin-style naming).
- Do **not** use BaseTestClass patterns.
- Use NSubstitute for mocks.
- Prefer DI + in-memory profiles for fast tests.

## Related Resources
- `../aggregate/` (domain)
- `../projection/` (queries)
- `../controller/` (HTTP adapters)
