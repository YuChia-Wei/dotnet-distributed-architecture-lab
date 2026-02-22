# Use Case Contract Example (.NET)

## Overview
Use case contracts validate input and ensure expected outcomes.

## Example: Create Task Use Case
```csharp
public sealed class CreateTaskService : ICreateTaskUseCase
{
    private readonly IRepository<Plan, PlanId> _repository;

    public CreateTaskService(IRepository<Plan, PlanId> repository)
    {
        Contract.RequireNotNull(nameof(repository), repository);
        _repository = repository;
    }

    public async Task<CqrsOutput> ExecuteAsync(CreateTaskInput input, CancellationToken ct)
    {
        Contract.RequireNotNull("input", input);
        Contract.RequireNotNull("planId", input.PlanId);
        Contract.RequireNotNull("projectName", input.ProjectName);
        Contract.Require(!string.IsNullOrWhiteSpace(input.TaskName), "Task name required");

        var plan = await _repository.FindByIdAsync(input.PlanId, ct);
        Contract.Require(plan != null, "Plan must exist");

        var oldVersion = Contract.Old(() => plan!.Version);

        plan!.CreateTask(input.ProjectName, input.TaskName);
        await _repository.SaveAsync(plan, ct);

        Contract.Ensure(plan.Version == oldVersion + 1, "Version incremented");

        return CqrsOutput.Success(plan.Id.Value);
    }
}
```

## Contract Tips for Use Cases

- Validate input DTOs at the boundary.
- Ensure repository results are not null.
- Verify expected domain events or output values.
