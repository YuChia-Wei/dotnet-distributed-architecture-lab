# .NET DDD WolverineFx Best Practices

## Overview

This document summarizes the best practices to follow in the .NET DDD + WolverineFx + EF Core technology stack.

## Domain Modeling Best Practices

### 1. ✅ Small, Focused Aggregates
```csharp
public sealed class Plan : AggregateRoot
{
    private PlanId _id;
    private PlanName _name;
    private UserId _ownerId;
    private readonly List<Project> _projects = new();

    public ProjectId CreateProject(string name)
    {
        Contract.Require("Project name", () => name is not null);
        var projectId = ProjectId.New();
        Apply(new ProjectCreated(_id.Value, projectId.Value, name));
        return projectId;
    }
}
```

### 2. ✅ Rich Value Objects
```csharp
public sealed record Email
{
    public string Value { get; }

    public Email(string value)
    {
        Contract.Require("Email", () => value is not null);
        if (!IsValid(value))
        {
            throw new ArgumentException("Invalid email format", nameof(value));
        }
        Value = value.ToLowerInvariant();
    }

    private static bool IsValid(string email)
        => Regex.IsMatch(email, "^[A-Za-z0-9+_.-]+@(.+)$");
}
```

### 3. ✅ Explicit Domain Events
```csharp
public static class PlanEvents
{
    public sealed record TaskMovedToProject(
        string PlanId,
        string TaskId,
        string FromProjectId,
        string ToProjectId,
        IDictionary<string, string> Metadata
    ) : IDomainEvent;
}
```

## Application Layer Best Practices

### 4. ✅ Thin Use Case Layer
```csharp
public sealed class CreatePlanHandler
{
    private readonly IAggregateRepository<Plan, PlanId> _repository;

    public async Task<CqrsOutput<PlanDto>> Handle(CreatePlanInput input)
    {
        var plan = new Plan(PlanId.New(), input.Name, input.UserId);
        await _repository.Save(plan);
        return CqrsOutput.Of(PlanMapper.ToDto(plan));
    }
}
```

### 5. ✅ Clear Input and Output DTOs
```csharp
public sealed record CreateTaskInput(
    string PlanId,
    string ProjectId,
    string TaskName,
    string Description,
    DateOnly? Deadline);
```

### 6. ✅ Use a Reactor/Handler Across Aggregates
```csharp
public sealed class UnassignTaskWhenTagDeleted
{
    private readonly IFindPlansByTagIdInquiry _inquiry;
    private readonly IAggregateRepository<Plan, PlanId> _planRepository;

    public async Task Handle(TagDeleted e)
    {
        var planIds = await _inquiry.FindByTagId(e.TagId);
        foreach (var planId in planIds)
        {
            var plan = await _planRepository.FindById(planId);
            if (plan is null) continue;
            plan.RemoveTagFromAllTasks(e.TagId, e.UserId);
            await _planRepository.Save(plan);
        }
    }
}
```

## Testing Best Practices

### 7. ✅ BDD-Style Tests
```gherkin
Feature: Create Plan
  Scenario: Successfully create a plan
    Given a valid plan input
    When the create plan use case is executed
    Then a new plan should be created
```

```csharp
public sealed class CreatePlanSteps
{
    [Given(@"a valid plan input")]
    public void GivenValidInput() { /* ... */ }
}
```

### 8. ✅ Use a Test Data Builder
```csharp
public sealed class PlanTestDataBuilder
{
    private string _name = "Default Plan";
    private string _userId = "user123";

    public static PlanTestDataBuilder APlan() => new();
    public PlanTestDataBuilder WithName(string name) { _name = name; return this; }
    public Plan Build() => new(PlanId.New(), _name, _userId);
}
```

## Persistence Best Practices

### 9. ✅ Strictly Follow Repository Restrictions
- A Repository permits only findById / save / delete.
- Use a Projection/Inquiry for queries.

### 10. ✅ Explicit Data Mapping
```csharp
public static class PlanMapper
{
    public static PlanData ToData(Plan plan) => new()
    {
        Id = plan.Id.Value,
        Name = plan.Name.Value
    };

    public static PlanDto ToDto(Plan plan) => new(plan.Id.Value, plan.Name.Value);
}
```

### 11. ✅ Optimize Queries with Projections
```csharp
public sealed class PlanSummaryProjection
{
    private readonly DbContext _db;

    public Task<List<PlanSummaryDto>> Query(string userId)
        => _db.Set<PlanData>()
            .Where(p => p.UserId == userId)
            .Select(p => new PlanSummaryDto(p.Id, p.Name))
            .AsNoTracking()
            .ToListAsync();
}
```

## Architecture Best Practices

### 12. ✅ Use Constructor Injection
Use constructor injection and avoid the Service Locator pattern.

### 13. ✅ Generate Timestamps with DateProvider / TimeProvider
Use a testable time source for all Domain Events.

### 14. ✅ Consistent Error Handling
Use `ProblemDetails` or global exception-handling middleware.

## Performance Best Practices

### 15. ✅ Use Caching Appropriately
Use `IMemoryCache` or a distributed cache for hot data.

### 16. ✅ Optimize Batch Operations
When necessary, reduce round trips with batch queries and batch saves.

## Development Workflow Best Practices

### 17. ✅ Follow the TDD Cycle
Red → Green → Refactor.

### 18. ✅ Keep Documentation Current
Synchronize specification changes with `.dev/specs` and examples.

### 19. ✅ Protect BDD Specifications
Gherkin-style scenario names represent business rules. When a test fails, identify the cause before changing them.

### 20. ✅ Code Review Checklist
- [ ] Domain logic resides in the Domain layer.
- [ ] The Use Case is sufficiently thin.
- [ ] Event names express business meaning.
- [ ] Tests cover the primary scenarios.
- [ ] Established coding standards are followed.

## Summary

Core best-practice principles:
1. Domain first.
2. Keep it simple and explicit.
3. Test-driven development.
4. Continuous improvement.
