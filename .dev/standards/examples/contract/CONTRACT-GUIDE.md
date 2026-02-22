# Contract Design Guide (.NET)

## Overview

Design by Contract defines:
- Preconditions: what must be true before a method executes
- Postconditions: what must be true after it executes
- Invariants: what must always be true for an object

In DDD and Event Sourcing, contracts protect invariants and keep domain
state consistent.

## Core Concepts

### Preconditions
- Validate input parameters
- Validate current state
- Use `Require` and `RequireNotNull`

### Postconditions
- Validate expected state changes
- Validate emitted events
- Use `Ensure`

### Invariants
- Validate long-lived rules
- Use `Invariant` and `InvariantNotNull`
- Run after public operations

## Principles

1. **Precision**: contract checks must be specific.
2. **Completeness**: check all required inputs and outcomes.
3. **Minimality**: avoid redundant checks.
4. **Readability**: use clear error messages.

## Anti-Patterns

### Redundant Checks
```csharp
// Wrong: getter == field is meaningless
Contract.Ensure(Color == _color, "Color unchanged");
```

### Duplicate State Checks
```csharp
public void Rename(string newName)
{
    Contract.Require(!IsDeleted, "Not deleted");
    // ...
    Contract.Ensure(!IsDeleted, "Still not deleted"); // redundant
}
```

### Checking Immutable Data
```csharp
// Wrong: ID never changes, no need to check
Contract.Ensure(Id == id, "ID unchanged");
```

## Advanced Features (uContract)

### Old State
```csharp
var oldVersion = Contract.Old(() => Version);
```

### EnsureAssignable
```csharp
var oldUser = Contract.Old(() => this.Clone());
Email = newEmail;
Contract.EnsureAssignable(this, oldUser, "Email", "LastModified");
```

### EnsureResult
```csharp
return Contract.EnsureResult(user, u => u != null && u.IsActive);
```

### Reject
```csharp
if (Contract.Reject("Name unchanged", () => Name == newName))
{
    return;
}
```

### Check
```csharp
Contract.Check("Payment validated", () => validated);
```

## Checklist

- [ ] Preconditions validate all inputs and state
- [ ] Only store old values that can change
- [ ] Postconditions verify real effects
- [ ] Invariants are always enforced
- [ ] Error messages are actionable
