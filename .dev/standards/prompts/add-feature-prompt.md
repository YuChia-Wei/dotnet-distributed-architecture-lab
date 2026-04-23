# Prompt Template: Add New Feature (Dotnet)

> Migration note:
> This file is a legacy human-facing prompt example.
> Canonical reusable prompt assets should live under `.ai/` and `.ai/assets/`.

## Input Format
```yaml
feature_name: Task Priority
feature_description: Add priority levels (High, Medium, Low) to tasks
affected_aggregates:
  - Plan (add priority field to tasks)
  - Task (new priority property)
required_use_cases:
  - SetTaskPriority
  - GetTasksByPriority
ui_changes:
  - Add priority selector in task creation
  - Show priority badge on task items
  - Add filter by priority
```

## Generation Steps

### Step 1: Update Domain Model
1. Add new value object if needed (e.g., `TaskPriority`).
2. Update aggregate with new field (Apply/When only).
3. Add domain methods for the feature.
4. Update domain events and metadata.

### Step 2: Create Use Cases
For each required use case:
1. Create use case handler and input model.
2. Implement business logic.
3. Write xUnit + BDDfy tests (Gherkin-style naming).

### Step 3: Update Persistence
1. Add EF Core migration if needed.
2. Update entity mappings (owned types, collections).
3. Update mappers/serialization if needed.

### Step 4: Create/Update API Endpoints
1. Create new controllers or update existing.
2. Add DTOs (separate files) under `src/Api/Contracts/...`.
3. Update OpenAPI documentation (if used).

### Step 5: Update Frontend (if required)
1. Update API client (RTK Query).
2. Add/modify React components.
3. Update state/cache/optimistic rules if needed.

## Example Code Structure

### Value Object
```csharp
public sealed record TaskPriority(string Value)
{
    public static readonly TaskPriority High = new("HIGH");
    public static readonly TaskPriority Medium = new("MEDIUM");
    public static readonly TaskPriority Low = new("LOW");

    public TaskPriority
    {
        // TODO: replace with Objects/Guard rules per common-rules
        if (!IsValid(Value)) throw new ArgumentException("Invalid priority", nameof(Value));
    }

    private static bool IsValid(string value)
        => value is "HIGH" or "MEDIUM" or "LOW";
}
```

### Domain Method
```csharp
public void SetPriority(TaskId taskId, TaskPriority priority, string userId)
{
    Contract.Require("TaskId", () => taskId != null);
    Contract.Require("Priority", () => priority != null);
    // TODO: require task existence

    Apply(new TaskPrioritySet(
        Id.Value,
        taskId.Value,
        priority.Value,
        DateProvider.Now(),
        new Dictionary<string, string> { ["userId"] = userId }
    ));
}
```

## Validation Points
- [ ] Domain model updated correctly
- [ ] All use cases implemented and tested
- [ ] EF Core migrations created if needed
- [ ] API endpoints working
- [ ] Frontend integrated (if applicable)
- [ ] All tests passing
