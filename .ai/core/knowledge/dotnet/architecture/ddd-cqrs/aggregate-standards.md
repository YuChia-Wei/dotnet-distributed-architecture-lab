# Aggregate Coding Standards (.NET)

This document defines coding standards for Aggregates, Entities, Value Objects, and Domain Events.

Contract semantics are defined in
[Design By Contract Semantics](../../core/design-by-contract.md). Names such as
`Contract.Require` and `Contract.Ensure` in snippets are illustrative helper
names, not a required package API.

---

## 📌 Overview

An Aggregate is a core DDD model and MUST preserve its invariants. Event Sourcing
is an explicit Aggregate profile, not a requirement for every Aggregate.

- The **Aggregate Root** is the only public modification entry point.
- A normal Aggregate implements `IAggregateRoot<TId>` directly and may keep
  current state without replay mechanics.
- An event-sourced Aggregate derives from or behaviorally implements
  `EsAggregateRoot<TId>` and records state changes through Domain Events.
- **Immutability**: Value Objects MUST be immutable.
- **Transaction boundary**: one Command modifies one Aggregate by default. Coordinate
  other Aggregates through events and eventual consistency. A same-boundary
  multi-Aggregate transaction is an exceptional, documented decision governed by
  [Use Case Standards](usecase-standards.md#7-strong-consistency-must-be-explicit),
  not a general implementation template.

---

## 🏷️ Automated Check Boundaries

`DBA1009` and `DBA1003` are optional product binding labels; Framework supplies
no Analyzer implementation. Do not use type/method names as proof of current
product predicates. The [versioned comparison](../../references/policy-rationale.md#versioned-archprecept-comparison-not-a-second-rule-catalog)
records ArchPrecept source `60330242f7f690a01cfa2332b578aac35584f067`, including
DBA1009's recognized ES role and canonical transition override identity. It is
not evidence of a published package or target adoption. Invariant completeness,
event completeness and deletion-policy adoption still need target tests/review.

Rule IDs: `AGGREGATE-ES-001`, `DELETE-SOFT-001`,
`CONTRACT-SEMANTICS-001`.

```yaml
normal-aggregate:
  type: IAggregateRoot<TId>
  apply-when-required: false
event-sourced-aggregate:
  type: EsAggregateRoot<TId>
  apply-when-required: true
  optional-target-analyzer-binding: DBA1009
all-aggregates:
  optional-target-infrastructure-binding: DBA1003
```

---

## ⚠️ Critical Warning: Collection Field Initialization Timing

**Problem**: Initializing a collection field in the constructor after `base()` clears data restored by event replay.

```csharp
// ❌ Incorrect: Replay can dispatch When before _members is initialized here
public class DeliveryTeam : EsAggregateRoot<DeliveryTeamId>
{
    private readonly List<TeamMember> _members;

    public DeliveryTeam(IEnumerable<IDomainEvent> domainEvents)
    {
        Replay(domainEvents);
        _members = new List<TeamMember>();  // Too late for replay transitions
    }
}

// ✅ Correct: initialize at field declaration
public class DeliveryTeam : EsAggregateRoot<DeliveryTeamId>
{
    private readonly List<TeamMember> _members = new();  // Correct initialization timing

    public DeliveryTeam(IEnumerable<IDomainEvent> domainEvents)
    {
        Replay(domainEvents); // called from the derived constructor body
    }
}
```

---

## 🔴 Active Rules

### 0. Soft-Delete Default Profile

Rule ID: `DELETE-SOFT-001` (`profile-default`).

The dotnet-backend Aggregate Repository profile defaults to soft deletion.
Affected Aggregates support the following field and event-application behavior,
and deletion is persisted through `SaveAsync`.

A target may explicitly opt out for an Aggregate or repository profile when its
requirements or architecture decision select another lifecycle. The opt-out
must be recorded in target evidence such as `.dev/project-config.yaml`
architecture capability selections, requirements, or an ADR. An opted-out
Aggregate is not required to add `IsDeleted`.

#### Adopted Aggregate Root Must Have an `IsDeleted` Field and Handling Logic

```csharp
// ✅ Correct when soft deletion is adopted
public class WorkItem : EsAggregateRoot<WorkItemId>
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
    Apply(new TaskCreated(Id, taskId, name, estimatedHours, creatorId, DateProvider.Now()));

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
// ✅ Normal state-based Aggregate: no shared base class required
public class Product : IAggregateRoot<ProductId>
{
    public ProductId Id { get; }

    // Product-owned behavior and invariants.
    // Apply/When and replay mechanics are not required.
}

// ✅ Event-sourced Aggregate: the only optional supplied base class
public class EventSourcedProduct : EsAggregateRoot<ProductId>
{
    public override ProductId Id { get; }

    // Required event transition:
    protected override void When(IDomainEvent @event) { ... }

    public string Name { get; private set; } = string.Empty;
    public ProductState State { get; private set; }
    public bool IsDeleted { get; private set; }
}
```

Do not introduce `DomainEntity<TId>`, non-ES `AggregateRoot<TId>`, or
`ValueObject` base classes as default requirements. See the
[BuildingBlocks Reconstruction Contract](building-blocks-reconstruction.md).

### Creation and Rehydration Responsibilities

Creation produces new facts and checks current command preconditions. Rehydration
restores already accepted state/history under selected schema/event-version and
compatibility rules, without producing new pending events or external effects.
Do not invoke creation commands to rebuild state and then erase their events.
Historical transitions do not rerun today's command preconditions; unsupported
versions and missing required business state still fail explicitly. An identity
is insufficient proof of completeness. A failed/partly mutated reconstruction
returns no usable Aggregate; discard it and route repair to the target data owner.

State rehydration can use a dedicated constructor accepting validated complete
persisted state. ES reconstruction uses the selected replay entrypoint after
initialization. `Replay` below is the package-free ES snippet API;
ArchPrecept CT-005 uses `LoadFromHistory`. Neither justifies a universal Clear.
See [mapper lifecycle](../../integration/persistence/mapper-standards.md#pending-domain-events-after-reconstruction)
and the [contract cases](../../testing/reconstruction-and-projector-cases.md).

### 2. Constructor Design

The retained profile uses public constructors and rejects static Aggregate
factories. This form restriction lacks sufficient rationale for universal use;
it is not a DDD theorem. [Factory comparison](../../references/policy-rationale.md#factory-retained-policy-and-unresolved-justification)
keeps alternatives unselected pending owner decision. Every creation path must
complete invariants; rehydration is a separate lifecycle and cannot bypass state.

```csharp
// ✅ Correct: provide two constructors
public class Product : EsAggregateRoot<ProductId>
{
    private readonly List<Task> _tasks = new();  // Initialize at field declaration

    // Constructor for Event Sourcing reconstruction
    public Product(IEnumerable<IDomainEvent> events)
    {
        Replay(events);
    }

    // Public constructor for creating a new instance
    public Product(ProductId id, string name, string creatorId)
    {
        ArgumentNullException.ThrowIfNull(id);
        ArgumentException.ThrowIfNullOrEmpty(name);
        ArgumentException.ThrowIfNullOrEmpty(creatorId);

        Apply(new ProductCreated(id, name, creatorId, DateProvider.Now()));

        // Postconditions
        Contract.Ensure(Id.Equals(id), "ID must be set");
        Contract.Ensure(Name == name, "Name must be set");
    }
}

// Outside this retained profile: static Aggregate factory (not a universal DDD violation)
public static Product Create(ProductId id, string name)
{
    // Requires an explicit owner decision before changing this profile
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
    Apply(new ProductRenamed(Id, newName, DateProvider.Now()));

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

Value semantics exclude conceptual identity; immutable treatment protects shared
values from unexpected change. A record or readonly reference does not prove
deep immutability. ArchPrecept DBA1018/1019 are stricter bounded product policies;
retain unknown/not-evaluated results and consult the [versioned VO comparison](../../references/policy-rationale.md#value-objects-and-bounded-product-checks).

```csharp
// ✅ Correct: return a new instance
public Money Add(Money other)
{
    if (Currency != other.Currency)
        throw new InvalidOperationException("Currency mismatch");
    return this with { Amount = Amount + other.Amount };
}

// Incorrect: mutate value state; record syntax alone does not prevent mutable members
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

Trace invariants through construction, public transitions and failures. Use
fixtures with valid initial state, observe postconditions and keep expected
values independent. Where an operation emits events, check immutable event
intent and required identity/trace metadata. Where the target selects ES or
a persistence round trip, exercise replay or serialization separately. Accept
a target-owned equivalent API when the adopted contract allows it.

### Aggregate Root
- [ ] Implements `IAggregateRoot<TId>` directly, or uses
      `EsAggregateRoot<TId>` only when Event Sourcing is selected.
- [ ] Does not require another shared Aggregate/Entity/ValueObject base class.
- [ ] If event-sourced, provides a reconstruction constructor that calls
      `Replay(history)` from the derived constructor body.
- [ ] Provides a public constructor, not a static factory.
- [ ] If event-sourced, implements
      `protected override void When(IDomainEvent @event)`.
- [ ] Has an `IsDeleted` field under the default soft-delete profile, or records an explicit target opt-out.
- [ ] Command methods check preconditions.
- [ ] Command methods check postconditions.
- [ ] Required reconstruction state and versions are validated; failures expose
      no usable partial Aggregate and have an identifiable repair owner.
- [ ] Historical transitions do not re-run current creation preconditions or
      external effects; pending/commit behavior follows the selected protocol.
- [ ] If event-sourced, applies Domain Events correctly (`Apply`).
- [ ] If event-sourced, collection fields are initialized before `Replay` and
      replay is not initiated from a base constructor.
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

## Related Documents

- [usecase-standards.md](usecase-standards.md)
- [mapper-standards.md](../../integration/persistence/mapper-standards.md)
- [repository-standards.md](../../integration/persistence/repository-standards.md)
- [test-standards.md](../../testing/test-standards.md)
- [BuildingBlocks Reconstruction Contract](building-blocks-reconstruction.md)
- [Design By Contract Semantics](../../core/design-by-contract.md)
