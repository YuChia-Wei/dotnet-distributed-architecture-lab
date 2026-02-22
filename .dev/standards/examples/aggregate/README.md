# Aggregate Examples and Patterns (.NET)

This folder contains Aggregate Root design notes and example implementations.

## Overview

Aggregate Roots define consistency and transaction boundaries in DDD. Under event sourcing, an Aggregate Root
handles commands, emits domain events, and rebuilds state from those events.

## Core Concepts

- **Consistency boundary**: invariants must hold within an aggregate.
- **Transaction boundary**: changes to an aggregate happen in one transaction.
- **Aggregate Root**: external access goes through the root only.

### Event Sourcing
- State changes are recorded as events.
- State can be rebuilt by replaying events.
- Supports auditing and time travel.

## File Layout

```
aggregate/
├── README.md             # This guide
├── Plan.cs               # Plan aggregate root example
├── Project.cs            # Project entity inside Plan
├── PlanEvents.cs         # Plan domain events (all in one file)
├── PlanId.cs             # Plan ID value object
├── ProjectId.cs          # Project ID value object
├── ProjectName.cs        # Project name value object
├── TaskId.cs             # Task ID value object
├── TagId.cs              # Tag ID value object
└── TagEvents.cs          # Tag domain events (all in one file)
```

### IMPORTANT: Domain Events Must Stay in One File
Do **not** create a file per event. Keep all events inside `PlanEvents.cs` / `TagEvents.cs`:
- Correct: `PlanEvents.cs` contains `PlanCreated`, `PlanRenamed`, `PlanDeleted`, ...
- Incorrect: `PlanCreated.cs`, `PlanRenamed.cs`, ...

## Entity vs Aggregate Root

Entities have identity but are not aggregate roots. They must be accessed via the root.

| Feature | Entity (Project) | Value Object (ProjectName) |
|--------|-------------------|---------------------------|
| Identity | Has ID | No ID, value-based |
| Mutability | Mutable | Immutable |
| Lifecycle | Has | None |
| Equality | By ID | By value |

## Value Objects

Value objects are immutable, have no identity, and encapsulate domain rules.

Example (C#):

```csharp
public sealed record ProjectName
{
    public string Value { get; }

    public ProjectName(string value)
    {
        if (string.IsNullOrWhiteSpace(value))
        {
            throw new ArgumentException("ProjectName cannot be empty.", nameof(value));
        }
        Value = value;
    }

    public static ProjectName ValueOf(string value) => new(value);
    public override string ToString() => Value;
}
```

## Implementation Notes

### Aggregate Root Structure

```csharp
public sealed class Plan : EsAggregateRoot<PlanId, PlanEvents.IPlanEvent>
{
    public const string Category = "Plan";

    public Plan(IEnumerable<PlanEvents.IPlanEvent> events) : base(events) { }

    public Plan(PlanId planId, string name, string userId)
    {
        Contract.RequireNotNull("Plan id", planId);
        Contract.RequireNotNull("Plan name", name);
        Contract.RequireNotNull("User id", userId);

        Apply(new PlanEvents.PlanCreated(
            planId,
            name,
            userId,
            new Dictionary<string, string>(),
            Guid.NewGuid(),
            DateProvider.Now()
        ));
    }
}
```

### Domain Behavior

```csharp
public void Rename(string newName)
{
    Contract.RequireNotNull("New name", newName);
    Contract.Require("New name not empty", () => !string.IsNullOrWhiteSpace(newName));
    Contract.Require("New name is different", () => Name != newName);

    Apply(new PlanEvents.PlanRenamed(
        Id,
        newName,
        new Dictionary<string, string>(),
        Guid.NewGuid(),
        DateProvider.Now()
    ));
}
```

### Event Handlers

```csharp
protected override void When(PlanEvents.IPlanEvent @event)
{
    switch (@event)
    {
        case PlanEvents.PlanCreated e:
            _id = e.PlanId;
            _name = e.Name;
            _userId = e.UserId;
            _isDeleted = false;
            break;
        case PlanEvents.PlanRenamed e:
            _name = e.NewName;
            break;
        case PlanEvents.PlanDeleted:
            _isDeleted = true;
            break;
    }
}
```

### Invariants

```csharp
public override void EnsureInvariant()
{
    Contract.Invariant("Category matches", () => Category == "Plan");
    Contract.InvariantNotNull("Plan Id", _id);
    if (!_isDeleted)
    {
        Contract.InvariantNotNull("Plan Name", _name);
        Contract.InvariantNotNull("User Id", _userId);
    }
}
```

## Design Rules

- All state changes must come from `Apply(event)`.
- Do not set state directly outside `When(...)`.
- Keep events immutable.
- Avoid overgrown aggregates; split when necessary.

## Related Examples
- `../usecase/` - Use case patterns
- `../controller/` - API controllers
- `../projection/` - CQRS projections
- `../dto/` - DTO templates
- `../mapper/` - Mapping patterns
- `../test/` - Testing patterns
- `../contract/` - Design by Contract examples
