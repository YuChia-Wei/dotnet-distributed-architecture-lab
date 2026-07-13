# Aggregate Coding Standards (.NET)

This document defines coding standards for Aggregates, Entities, Value Objects, and Domain Events.

---

## 📌 Overview

An Aggregate is a core DDD model and MUST follow the Event Sourcing and invariant-preservation rules.

- The **Aggregate Root** is the only public modification entry point.
- **State changes** are recorded through Domain Events.
- **Immutability**: Value Objects MUST be immutable.
- **Transaction boundary**: one Command modifies one Aggregate by default. Coordinate
  other Aggregates through events and eventual consistency. A same-boundary
  multi-Aggregate transaction is an exceptional, documented decision governed by
  [Use Case Standards](usecase-standards.md#7-strong-consistency-must-be-explicit),
  not a general implementation template.

---

## 🏷️ Pattern Markers for Automated Checks

The following markers are consumed by automated code-review scripts:

```yaml
# Aggregate Root rules
Pattern (required): Apply\(
Pattern (required): protected override void When
Pattern (required): Ensure\.|Contract\.|Guard\.
Pattern (optional): IsDeleted

# Forbidden rules
Pattern (forbidden, ignore-comment): DbContext
Pattern (forbidden): new .*Service\(
```

---

## ⚠️ Critical Warning: Collection Field Initialization Timing

**Problem**: Initializing a collection field in the constructor after `base()` clears data restored by event replay.

```csharp
// ❌ Incorrect: clears event-replayed data
public class ScrumTeam : AggregateRoot<ScrumTeamId>
{
    private readonly List<TeamMember> _members;
    
    public ScrumTeam(IEnumerable<IDomainEvent> domainEvents) : base(domainEvents)
    {
        _members = new List<TeamMember>();  // Incorrect: clears the data that was just replayed
    }
}

// ✅ Correct: initialize at field declaration
public class ScrumTeam : AggregateRoot<ScrumTeamId>
{
    private readonly List<TeamMember> _members = new();  // Correct initialization timing
    
    public ScrumTeam(IEnumerable<IDomainEvent> domainEvents) : base(domainEvents)
    {
        // _members already exists, so event replay data is preserved
    }
}
```

---

## 🔴 Active Rules

### 0. Soft-Delete Field Requirement

Rule ID: `DELETE-SOFT-001` (`conditional`).

When target-repository requirements or an architecture decision explicitly adopt
aggregate soft deletion, each affected Aggregate must support the following
field and event-application behavior. Aggregates are not required to add an
`IsDeleted` field when the capability is not selected.

#### Adopted Aggregate Root Must Have an `IsDeleted` Field and Handling Logic

```csharp
// ✅ Correct when soft deletion is adopted
public class WorkItem : AggregateRoot<WorkItemId>
{
    public bool IsDeleted { get; private set; }  // Required soft-delete marker
    
    // Set IsDeleted = true when handling the deletion event
    protected override void When(IDomainEvent @event)
    {
        switch (@event)
        {
            case WorkItemDeleted e:
                IsDeleted = true;  // Mark as deleted
                break;
            // Other event handling...
        }
    }
}
```

---

### 1. Aggregate Command-Method Postcondition Checks

**Mandatory**: Every Aggregate command method MUST use Guard Clauses or Contracts to verify:
1. correctness of the business-state change;
2. correctness of Domain Event generation.

```csharp
// ✅ Correct: complete postcondition checks
public void CreateTask(TaskId taskId, string name, int? estimatedHours, string creatorId)
{
    // Preconditions
    ArgumentNullException.ThrowIfNull(taskId);
    ArgumentException.ThrowIfNullOrEmpty(name);
    
    // Apply domain event
    Apply(new TaskCreated(Id, taskId, name, estimatedHours, creatorId, DateTime.UtcNow));
    
    // Postconditions: verify business state
    var createdTask = _tasks.FirstOrDefault(t => t.Id.Equals(taskId));
    
    Contract.Ensure(createdTask is not null, "Task must be created");
    Contract.Ensure(createdTask!.Id.Equals(taskId), "Task ID must be set");
    Contract.Ensure(createdTask.Name == name, "Task name must be set");
    Contract.Ensure(createdTask.State == TaskState.Todo, "Task initial state must be TODO");
    
    // Postconditions: verify Domain Event correctness
    var lastEvent = GetLastDomainEvent();
    Contract.Ensure(
        lastEvent is TaskCreated created && 
        created.TaskId.Equals(taskId) && 
        created.Name == name,
        "TaskCreated event must be generated correctly"
    );
}
```

---

### 2. Validation-Method Selection Rules

| Component Type | Validation Method | Description |
|---------|---------|------|
| Aggregate Root | Guard Clauses + Contracts | `Contract.Require()`, `Contract.Ensure()` |
| Entity | `ArgumentNullException.ThrowIfNull` | Standard .NET 7+ method |
| Value Object | `ArgumentNullException.ThrowIfNull` | Standard .NET 7+ method |
| Domain Event | `ArgumentNullException.ThrowIfNull` | Validate in the record constructor |

---

## 🎯 Aggregate Root Design Principles

### 1. Inheritance Rules

```csharp
// ✅ Event Sourcing Aggregate
public class Product : AggregateRoot<ProductId>
{
    // Required implementation:
    protected override void When(IDomainEvent @event) { ... }
    
    // Properties
    public ProductId Id { get; private set; }
    public string Name { get; private set; } = string.Empty;
    public ProductState State { get; private set; }
    public bool IsDeleted { get; private set; }
}
```

### 2. Constructor Design

```csharp
// ✅ Correct: provide two constructors
public class Product : AggregateRoot<ProductId>
{
    private readonly List<Task> _tasks = new();  // Initialize at field declaration
    
    // Constructor for Event Sourcing reconstruction
    public Product(IEnumerable<IDomainEvent> events) : base(events)
    {
    }
    
    // Public constructor for creating a new instance
    public Product(ProductId id, string name, string creatorId)
    {
        ArgumentNullException.ThrowIfNull(id);
        ArgumentException.ThrowIfNullOrEmpty(name);
        ArgumentException.ThrowIfNullOrEmpty(creatorId);
        
        Apply(new ProductCreated(id, name, creatorId, DateTime.UtcNow));
        
        // Postconditions
        Contract.Ensure(Id.Equals(id), "ID must be set");
        Contract.Ensure(Name == name, "Name must be set");
    }
}

// ❌ Incorrect: static factory method
public static Product Create(ProductId id, string name)
{
    // Do not use a static factory method
}
```

### 3. Command-Method Pattern

```csharp
public void Rename(string newName)
{
    // 1. Preconditions
    ArgumentException.ThrowIfNullOrEmpty(newName);
    Contract.Require(!IsDeleted, "Cannot rename deleted product");
    
    // 2. Avoid unnecessary events (optional)
    if (Name == newName)
        return;  // No update and no event
    
    // 3. Apply the event
    Apply(new ProductRenamed(Id, newName, DateTime.UtcNow));
    
    // 4. Postconditions
    Contract.Ensure(Name == newName, "Name must be updated");
    Contract.Ensure(
        GetLastDomainEvent() is ProductRenamed,
        "ProductRenamed event must be generated"
    );
}
```

---

## 🎯 Value Object Design Principles

### 1. Basic Structure

```csharp
// ✅ Use a record (recommended)
public sealed record ProductId(string Value)
{
    public ProductId() : this(Guid.NewGuid().ToString()) { }
    
    public static ProductId Create() => new();
    public static ProductId From(string value) => new(value);
    
    // Validate in the constructor
    public ProductId
    {
        ArgumentException.ThrowIfNullOrEmpty(Value);
    }
}

// ✅ Use a record struct (lightweight)
public readonly record struct Money(decimal Amount, string Currency)
{
    public Money Add(Money other)
    {
        if (Currency != other.Currency)
            throw new InvalidOperationException("Currency mismatch");
        return this with { Amount = Amount + other.Amount };
    }
}
```

### 2. Immutability Principle

```csharp
// ✅ Correct: return a new instance
public Money Add(Money other)
{
    if (Currency != other.Currency)
        throw new InvalidOperationException("Currency mismatch");
    return this with { Amount = Amount + other.Amount };
}

// ❌ Incorrect: mutate internal state (a record prevents this, but a class may not)
public void Add(Money other)
{
    Amount = Amount + other.Amount;  // Violates immutability
}
```

### 3. Constraint Validation

A Value Object SHOULD validate all business constraints during construction so an invalid instance cannot exist.

```csharp
// ✅ Correct: encapsulate range, length, and format constraints in constructors
public sealed record Quantity(int Value)
{
    public Quantity
    {
        ArgumentOutOfRangeException.ThrowIfNegativeOrZero(Value);
        ArgumentOutOfRangeException.ThrowIfGreaterThan(Value, 10_000);
    }
}

public sealed record ProductName(string Value)
{
    public ProductName
    {
        ArgumentException.ThrowIfNullOrEmpty(Value);
        if (Value.Length > 200)
            throw new ArgumentOutOfRangeException(nameof(Value), "Product name must not exceed 200 characters");
    }
}

public sealed record Email(string Value)
{
    private static readonly Regex EmailRegex = new(@"^[^@\s]+@[^@\s]+\.[^@\s]+$", RegexOptions.Compiled);

    public Email
    {
        ArgumentException.ThrowIfNullOrEmpty(Value);
        if (!EmailRegex.IsMatch(Value))
            throw new ArgumentException("Invalid email format", nameof(Value));
    }

    public static Email From(string value) => new(value);
}

// ✅ Composite constraint: validate multiple properties together
public sealed record DateRange(DateTime Start, DateTime End)
{
    public DateRange
    {
        if (End <= Start)
            throw new ArgumentException("End date must be later than start date");
    }

    public TimeSpan Duration => End - Start;
}
```

```csharp
// ❌ Incorrect: place constraint validation outside the Value Object (Application Layer or Entity)
public class PlaceOrderHandler
{
    public void Handle(int quantity)
    {
        if (quantity <= 0 || quantity > 10_000)  // The VO should encapsulate this constraint
            throw new ArgumentException();

        var q = new Quantity(quantity);  // The VO does not protect itself
    }
}
```

> **Principle**: If a value has business constraints such as range, length,
> format, or other rules, extract it as a Value Object and validate it during
> construction. This guarantees validity wherever the value is used (Make
> Illegal States Unrepresentable).

---

## 🎯 Domain Event Design Standards

### 1. Event Structure

```csharp
// ✅ Correct: use a sealed record
public sealed record ProductCreated(
    ProductId ProductId,
    string Name,
    string CreatorId,
    DateTime OccurredOn) : IDomainEvent
{
    public Guid EventId { get; } = Guid.NewGuid();
}

public sealed record ProductRenamed(
    ProductId ProductId,
    string NewName,
    DateTime OccurredOn) : IDomainEvent
{
    public Guid EventId { get; } = Guid.NewGuid();
}

public sealed record ProductDeleted(
    ProductId ProductId,
    string DeletedBy,
    DateTime OccurredOn) : IDomainEvent
{
    public Guid EventId { get; } = Guid.NewGuid();
}
```

### 2. Event Handler

```csharp
// ✅ Correct: handle events in When()
protected override void When(IDomainEvent @event)
{
    switch (@event)
    {
        case ProductCreated e:
            Id = e.ProductId;
            Name = e.Name;
            State = ProductState.Active;
            IsDeleted = false;
            break;
            
        case ProductRenamed e:
            Name = e.NewName;
            break;
            
        case ProductDeleted e:
            State = ProductState.Deleted;
            IsDeleted = true;
            break;
    }
}

// ❌ Incorrect: include business logic in an Event Handler
protected override void When(IDomainEvent @event)
{
    switch (@event)
    {
        case TaskAdded e:
            _tasks.Add(e.Task);
            // Incorrect: business logic does not belong in an Event Handler
            if (_tasks.Count > MaxTasks)
                throw new BusinessException("Too many tasks");
            break;
    }
}
```

---

## 🎯 Choosing Entity vs Value Object

### Choose an Entity When:
- It needs a unique identifier.
- It has a lifecycle.
- Its state changes.
- Examples: Task, Iteration, User.

### Choose a Value Object When:
- It is identified by its property values.
- It is immutable.
- It is replaceable.
- Examples: ProductId, Money, DateRange.

---

## 🔍 Checklist

### Aggregate Root
- [ ] Inherits `AggregateRoot<TId>`.
- [ ] Provides an Event Sourcing reconstruction constructor.
- [ ] Provides a public constructor, not a static factory.
- [ ] Implements `protected override void When(IDomainEvent @event)`.
- [ ] Has an `IsDeleted` field for soft deletion.
- [ ] Command methods check preconditions.
- [ ] Command methods check postconditions.
- [ ] Applies Domain Events correctly (`Apply`).
- [ ] Collection fields are initialized at declaration.
- [ ] The command changes one Aggregate by default.
- [ ] Cross-Aggregate effects use events and eventual consistency by default.
- [ ] Any exceptional same-boundary multi-Aggregate transaction satisfies and
      documents the strong-consistency criteria in
      [Use Case Standards](usecase-standards.md#7-strong-consistency-must-be-explicit).
- [ ] No transaction spans bounded contexts.

### Value Object
- [ ] Uses `record` or `record struct`.
- [ ] Is immutable.
- [ ] Has constructor validation.
- [ ] Uses `ArgumentNullException.ThrowIfNull`.

### Domain Event
- [ ] Uses a `sealed record`.
- [ ] Implements `IDomainEvent`.
- [ ] Includes the required Aggregate ID.
- [ ] Includes `OccurredOn` (`DateTime`).
- [ ] Includes `EventId` (`Guid`).

---

## 📂 Code Examples

For more complete examples, see:

| Example | Path |
|------|------|
| Aggregate examples | [../examples/aggregate/](../examples/aggregate/) |
| Domain Events | [../examples/aggregate/PlanEvents.cs](../examples/aggregate/PlanEvents.cs) |
| Value Objects | [../examples/aggregate/PlanId.cs](../examples/aggregate/PlanId.cs) |
| Outbox + Data examples | [../examples/outbox/](../examples/outbox/) |

---

## Related Documents

- [usecase-standards.md](usecase-standards.md)
- [mapper-standards.md](mapper-standards.md)
- [repository-standards.md](repository-standards.md)
- [test-standards.md](test-standards.md)
