# Use Case Patterns (.NET)

This folder shows Use Case patterns aligned with Clean Architecture.

## Overview

Use Cases are the application layer. Each Use Case:
- Encapsulates one business action
- Orchestrates Domain + Infrastructure
- Is framework-agnostic in its core logic

## Framework Concepts (Preserved)

Legacy patterns to avoid:
- `GenericInMemoryRepository` (replaced by Outbox + InMemory ORM)
- `BlockingMessageBus` (replaced by InMemory message broker)

These examples use local placeholder contracts rather than promising a future
shared package. Each target selects concrete packages and implementations while
preserving the architecture intent:
- Profile-based wiring (`TestInMemory` vs `TestOutbox`)
- Repository + Outbox with Wolverine + EF Core
- In-memory implementations for fast tests

## CQRS Command vs Query

### Command-style Use Case
Modifies state through an explicit Application inbound port:

```csharp
public interface ICreateTaskUseCase
{
    Task<CqrsOutput> ExecuteAsync(
        CreateTaskInput input,
        CancellationToken cancellationToken);
}

public sealed class CreateTaskUseCase : ICreateTaskUseCase
{
    public Task<CqrsOutput> ExecuteAsync(
        CreateTaskInput input,
        CancellationToken cancellationToken) { /* ... */ }
}
```

### Query-style Use Case
Reads data and returns a DTO or typed output:

```csharp
public sealed class GetPlansUseCase : IGetPlansUseCase
{
    public Task<GetPlansOutput> ExecuteAsync(
        GetPlansInput input,
        CancellationToken cancellationToken) { /* ... */ }
}
```

These examples intentionally contain no Handler because they do not define a real
dispatch/message entry. A Handler is a separate inbound adapter when such an entry
exists.

## Structure

```
usecase/
├── README.md
├── CreatePlanUseCaseContract.cs / CreatePlanUseCase.cs
├── CreateTaskUseCaseContract.cs / CreateTaskUseCase.cs
├── DeleteTaskUseCaseContract.cs / DeleteTaskUseCase.cs
├── RenameTaskUseCaseContract.cs / RenameTaskUseCase.cs
├── AssignTagUseCaseContract.cs / AssignTagUseCase.cs
├── GetPlanUseCaseContract.cs / GetPlanUseCase.cs
├── GetPlansUseCaseContract.cs / GetPlansUseCase.cs
├── GetTasksByDateUseCaseContract.cs / GetTasksByDateUseCase.cs
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
5. **Framework Boundary**
   Use Cases do not depend directly on Wolverine; Infrastructure adapts
   project-owned event publisher ports.

## Testing Notes

- Use xUnit + BDDfy (Gherkin-style naming).
- Do **not** use BaseTestClass patterns.
- Resolve `testing.mocking` from target technology selections; default to NSubstitute.
- Prefer DI + in-memory profiles for fast tests.

## Related Resources
- `../aggregate/` (domain)
- `../projection/` (queries)
- `../controller/` (HTTP adapters)
