# .NET DDD WolverineFx Anti-Patterns

## Overview

This document records common mistakes and anti-patterns to avoid in the .NET DDD + WolverineFx + EF Core technology stack.

When this learning-oriented summary conflicts with
[`coding-standards/`](coding-standards/) or
[`USECASE-COMMAND-HANDLER-RELATIONSHIP.MD`](USECASE-COMMAND-HANDLER-RELATIONSHIP.MD),
those canonical standards take precedence.

## Domain Layer Anti-Patterns

### 1. ❌ Anemic Domain Model
```csharp
// Incorrect: properties only, with business logic moved elsewhere
public sealed class User
{
    public string Id { get; init; }
    public string Name { get; set; }
    public string Email { get; set; }
}

public sealed class UserService
{
    public void ChangeEmail(User user, string newEmail)
    {
        if (!Email.IsValid(newEmail))
        {
            throw new ArgumentException("Invalid email");
        }
        user.Email = newEmail;
    }
}
```

✅ **Recommended approach**:
```csharp
public sealed class User : AggregateRoot
{
    private UserId _id;
    private UserName _name;
    private Email _email;

    public void ChangeEmail(string newEmail)
    {
        Contract.Require("Email", () => newEmail is not null);
        var email = new Email(newEmail); // Validation belongs in the Value Object
        Apply(new UserEmailChanged(_id.Value, email.Value, DateProvider.Now()));
    }

    private void When(UserEmailChanged e)
    {
        _email = new Email(e.Email);
    }
}
```

### 2. ❌ Oversized Aggregate
```csharp
// Incorrect: Company contains many collections
public sealed class Company
{
    public List<Employee> Employees { get; } = new();
    public List<Department> Departments { get; } = new();
    public List<Project> Projects { get; } = new();
}
```

✅ **Recommended approach**:
```csharp
public sealed class Company
{
    public CompanyId Id { get; init; }
    public CompanyName Name { get; init; }
}

public sealed class Employee
{
    public EmployeeId Id { get; init; }
    public CompanyId CompanyId { get; init; } // Reference by ID
}
```

### 3. ❌ Direct State Mutation
```csharp
// Incorrect: mutates state directly and bypasses events
public void Complete()
{
    _status = TaskStatus.Completed;
    _completedAt = DateTime.UtcNow;
}
```

✅ **Recommended approach**:
```csharp
public void Complete()
{
    if (_status == TaskStatus.Completed)
    {
        throw new InvalidOperationException("Task already completed");
    }
    Apply(new TaskCompleted(_id.Value, DateProvider.Now()));
}

private void When(TaskCompleted e)
{
    _status = TaskStatus.Completed;
    _completedAt = e.CompletedAt;
}
```

## Application Layer Anti-Patterns

### 4. ❌ Business Logic in a Use Case
```csharp
public sealed class CreateOrderUseCase
{
    public Task<CqrsOutput> ExecuteAsync(CreateOrderInput input)
    {
        // Incorrect: business rules belong in the Domain
        if (input.Items.Count == 0)
            throw new BusinessException("Order must have items");
        // ...
        return Task.FromResult(CqrsOutput.Success());
    }
}
```

✅ **Recommended approach**:
```csharp
public sealed class CreateOrderUseCase : ICreateOrderUseCase
{
    private readonly IAggregateRepository<Order, OrderId> _repository;

    public async Task<CqrsOutput> ExecuteAsync(
        CreateOrderInput input,
        CancellationToken cancellationToken)
    {
        var order = Order.Create(input.CustomerId, input.Items);
        await _repository.SaveAsync(order, cancellationToken);
        return CqrsOutput.Success();
    }
}
```

### 5. ❌ Cross-Aggregate Transaction
```csharp
// Incorrect: modifies multiple Aggregates in one transaction
public async Task TransferEmployee(string employeeId, string fromDeptId, string toDeptId)
{
    var employee = await _employeeRepo.FindById(employeeId);
    var fromDept = await _deptRepo.FindById(fromDeptId);
    var toDept = await _deptRepo.FindById(toDeptId);

    fromDept.RemoveEmployee(employee);
    toDept.AddEmployee(employee);
    employee.ChangeDepartment(toDeptId);

    await _deptRepo.Save(fromDept);
    await _deptRepo.Save(toDept);
    await _employeeRepo.Save(employee);
}
```

✅ **Recommended approach**:
```csharp
public async Task RequestTransfer(string employeeId, string toDeptId)
{
    var employee = await _employeeRepo.FindById(employeeId);
    employee.RequestTransfer(toDeptId);
    await _employeeRepo.Save(employee);
    // A WolverineFx handler/reactor coordinates synchronization across Aggregates
}
```

## Persistence Layer Anti-Patterns

### 6. ❌ Relying on Lazy Loading
```csharp
// Incorrect: relying on lazy loading produces an incomplete Aggregate
public class PlanData
{
    public virtual ICollection<TaskData> Tasks { get; set; } // lazy
}
```

✅ **Recommended approach**:
- Load Aggregates explicitly with `Include` or load them completely.
- Use a Projection/Read Model for queries to avoid overloading the Aggregate.

### 7. ❌ Adding Custom Query Methods to a Repository
```csharp
// Incorrect: do not add query methods to a Repository
public interface IUserRepository : IAggregateRepository<User, UserId>
{
    IEnumerable<User> FindByEmail(string email);
    IEnumerable<User> FindActiveUsers();
}
```

✅ **Recommended approach**:
- Keep only `FindByIdAsync` / `SaveAsync` on an Aggregate Repository.
- Use a read-only port that inherits `IQueryRepository` for queries.

### 8. ❌ Business Logic in a Repository
```csharp
public interface IUserRepository : IAggregateRepository<User, UserId>
{
    void DeactivateInactiveUsers(int days); // Business rule
}
```

✅ **Recommended approach**:
Place business logic in the Use Case or Domain. A Repository handles persistence only.

## Testing Anti-Patterns

### 9. ❌ Building a Custom In-Memory Implementation for Every Repository
```csharp
// Incorrect: a hand-written in-memory Repository can easily become inconsistent
public sealed class InMemoryPlanRepository : IPlanRepository
{
    private readonly Dictionary<string, Plan> _storage = new();
    public Task<Plan?> FindById(string id) => Task.FromResult(_storage.GetValueOrDefault(id));
    public Task Save(Plan plan) { _storage[plan.Id.Value] = plan; return Task.CompletedTask; }
}
```

✅ **Recommended approach**:
- Use the EF Core InMemory/SQLite provider with an Outbox.
- Alternatively, use Testcontainers with a real PostgreSQL instance.
- Tests must still honor the Aggregate Repository `FindByIdAsync` / `SaveAsync` contract.

### 10. ❌ Testing Implementation Details
```csharp
// Incorrect: tests a private field
Assert.True(ReflectionHelper.GetField(task, "_isCompleted"));
```

✅ **Recommended approach**: Verify behavior and events.

### 11. ❌ Excessive Mocking
```csharp
// Incorrect: too many mocks
var repo = Substitute.For<IAggregateRepository<Order, OrderId>>();
var eventPublisher = Substitute.For<IOrderEventPublisher>();
var mapper = Substitute.For<IMapper>();
```

✅ **Recommended approach**: Prefer real components or controlled infrastructure. Use the target-selected mocking library only for necessary interfaces; default to NSubstitute.

## Architecture Anti-Patterns

### 12. ❌ Bypassing Architecture Layers
```csharp
// Incorrect: a Controller accesses a Repository directly
[ApiController]
public sealed class UserController : ControllerBase
{
    private readonly IUserRepository _repository;

    [HttpGet("/users/{id}")]
    public async Task<User> Get(string id)
        => await _repository.FindById(id);
}
```

✅ **Recommended approach**: Controller → Use Case interface → Use Case implementation →
Domain / outbound ports. A Handler exists only at a real dispatch/message entry point.

## Performance Anti-Patterns

### 13. ❌ N+1 Queries
Use a Projection/Read Model or an appropriate EF Core query strategy to avoid N+1 queries.

### 14. ❌ Excessive Event Sourcing
Use a Projection for queries rather than replaying every event.

## Other Anti-Patterns

### 15. ❌ Direct Use of System Time APIs
Do not use `DateTime.UtcNow` directly in the Domain or events.

✅ **Recommended approach**:
```csharp
Apply(new PlanCreated(id, name, DateProvider.Now()));
```

### 16. ❌ Directly Changing BDD Specifications When Tests Fail
Gherkin-style scenario names represent business rules. When a test fails, first identify the cause and obtain human confirmation.

## Summary

The keys to avoiding anti-patterns are:
1. Keep the domain model rich.
2. Respect architecture layers and consistency boundaries.
3. Use Event Sourcing and CQRS correctly.
4. Test behavior rather than implementation details.
5. Use a testable time source (`DateProvider`/`TimeProvider`).
6. Respect test specifications; confirm before changing them when tests fail.
