# Projection Example (.NET)

This example shows how to implement a projection for cross-aggregate queries.

## Business Need
Query all pending tasks for a user, including plan/project names and tags.

## 1. Projection Interface
```csharp
public interface ITasksProjection
{
    Task<IReadOnlyList<TaskData>> QueryAsync(TasksProjectionInput input, CancellationToken ct);
}

public sealed class TasksProjectionInput
{
    public string? UserId { get; init; }
    public DateOnly? FromDate { get; init; }
    public DateOnly? ToDate { get; init; }
    public string? Status { get; init; } // PENDING, COMPLETED, ALL
}
```

## 2. Data Object (Persistence)
```csharp
public sealed class TaskData
{
    public string TaskId { get; set; } = string.Empty;
    public string TaskName { get; set; } = string.Empty;
    public DateOnly? Deadline { get; set; }
    public bool Completed { get; set; }
    public string PlanId { get; set; } = string.Empty;
    public string PlanName { get; set; } = string.Empty;
    public string ProjectId { get; set; } = string.Empty;
    public string ProjectName { get; set; } = string.Empty;
}
```

## 3. EF Core Projection
```csharp
public sealed class EfTasksProjection : ITasksProjection
{
    private readonly ReadModelDbContext _db;

    public EfTasksProjection(ReadModelDbContext db)
    {
        _db = db;
    }

    public async Task<IReadOnlyList<TaskData>> QueryAsync(
        TasksProjectionInput input,
        CancellationToken ct)
    {
        var query = _db.Tasks.AsQueryable();

        if (!string.IsNullOrWhiteSpace(input.UserId))
        {
            query = query.Where(t => t.UserId == input.UserId);
        }

        if (input.Status == "PENDING")
        {
            query = query.Where(t => !t.Completed);
        }
        else if (input.Status == "COMPLETED")
        {
            query = query.Where(t => t.Completed);
        }

        if (input.FromDate.HasValue)
        {
            query = query.Where(t => t.Deadline >= input.FromDate.Value);
        }
        if (input.ToDate.HasValue)
        {
            query = query.Where(t => t.Deadline <= input.ToDate.Value);
        }

        return await query.OrderBy(t => t.Deadline).ToListAsync(ct);
    }
}
```

## 4. InMemory Projection (for tests)
```csharp
public sealed class InMemoryTasksProjection : ITasksProjection
{
    private readonly List<TaskData> _store;

    public InMemoryTasksProjection(List<TaskData> store)
    {
        _store = store;
    }

    public Task<IReadOnlyList<TaskData>> QueryAsync(
        TasksProjectionInput input,
        CancellationToken ct)
    {
        var results = _store
            .Where(t => input.UserId == null || t.UserId == input.UserId)
            .Where(t => input.Status != "PENDING" || !t.Completed)
            .Where(t => input.Status != "COMPLETED" || t.Completed)
            .OrderBy(t => t.Deadline)
            .ToList();

        return Task.FromResult<IReadOnlyList<TaskData>>(results);
    }
}
```

## 5. Use in Use Case
```csharp
public sealed class GetTasksDueTodayService : IGetTasksDueTodayUseCase
{
    private readonly ITasksProjection _projection;

    public GetTasksDueTodayService(ITasksProjection projection)
    {
        _projection = projection;
    }

    public async Task<GetTasksDueTodayOutput> ExecuteAsync(
        GetTasksDueTodayInput input,
        CancellationToken ct)
    {
        var projectionInput = new TasksProjectionInput
        {
            UserId = input.UserId,
            FromDate = DateOnly.FromDateTime(DateTime.UtcNow),
            ToDate = DateOnly.FromDateTime(DateTime.UtcNow),
            Status = "PENDING"
        };

        var data = await _projection.QueryAsync(projectionInput, ct);
        return new GetTasksDueTodayOutput(data);
    }
}
```
