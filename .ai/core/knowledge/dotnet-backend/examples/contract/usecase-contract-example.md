# Use Case Contract Example (.NET)

## Overview
Use case contracts validate input and define expected outcomes. This example
uses standard .NET guards and leaves helper-package selection to the target.

## Example: Create Task Use Case
```csharp
public sealed class CreateTaskService : ICreateTaskUseCase
{
    private readonly IAggregateRepository<Plan, PlanId> _repository;

    public CreateTaskService(IAggregateRepository<Plan, PlanId> repository)
    {
        _repository = repository ?? throw new ArgumentNullException(nameof(repository));
    }

    public async Task<CreateTaskOutput> ExecuteAsync(
        CreateTaskInput input,
        CancellationToken ct)
    {
        ArgumentNullException.ThrowIfNull(input);
        ArgumentNullException.ThrowIfNull(input.PlanId);
        ArgumentException.ThrowIfNullOrWhiteSpace(input.ProjectName);
        ArgumentException.ThrowIfNullOrWhiteSpace(input.TaskName);

        var plan = await _repository.FindByIdAsync(input.PlanId, ct);
        if (plan is null)
        {
            throw new InvalidOperationException("Plan must exist.");
        }

        plan.CreateTask(input.ProjectName, input.TaskName);
        await _repository.SaveAsync(plan, ct);

        return new CreateTaskOutput(plan.Id.Value, plan.Version);
    }
}
```

## Contract Tips for Use Cases

- Validate input DTOs at the boundary.
- Ensure repository results are not null.
- Return operation-specific output rather than a framework placeholder.
- Use focused tests to verify the version change, expected Domain Event, output,
  and persisted Aggregate.
