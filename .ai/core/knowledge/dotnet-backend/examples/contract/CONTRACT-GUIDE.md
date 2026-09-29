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
- Validate input parameters and current state before mutation.
- Use standard guard clauses or a target-selected helper.

### Postconditions
- Validate expected state changes and emitted events.
- Use an explicit check or focused Domain test when runtime validation is not selected.

### Invariants
- Validate long-lived rules after public operations.
- Keep invariant checks free of Infrastructure I/O.

## Principles

1. **Precision**: contract checks must be specific.
2. **Completeness**: check all required inputs and outcomes.
3. **Minimality**: avoid redundant checks.
4. **Readability**: use clear error messages.

## Anti-Patterns

### Redundant Checks
```csharp
// Wrong: getter == field is meaningless
if (Color != _color) throw new InvalidOperationException("Color changed unexpectedly.");
```

### Duplicate State Checks
```csharp
public void Rename(string newName)
{
    if (IsDeleted) throw new InvalidOperationException("The entity is deleted.");
    // ...
    if (IsDeleted) throw new InvalidOperationException("The entity is deleted."); // redundant
}
```

### Checking Immutable Data
```csharp
// Wrong: ID never changes, no need to check
if (Id != id) throw new InvalidOperationException("ID changed unexpectedly.");
```

## Advanced Contract Techniques

### Old State
```csharp
var versionBefore = Version;
```

### Compare Allowed State Changes
```csharp
var userBefore = this.Clone();
Email = newEmail;
EnsureOnlyExpectedMembersChanged(this, userBefore, "Email", "LastModified");
```

`EnsureOnlyExpectedMembersChanged` is illustrative only; a target may use a
local helper, another guard mechanism, or focused tests to verify the same
promise.

### Validate A Result
```csharp
if (user is null || !user.IsActive) throw new InvalidOperationException("Active user is required.");
return user;
```

### Reject An Invalid Or No-Op Transition
```csharp
if (Name == newName)
{
    throw new InvalidOperationException("Name is unchanged.");
}
```

### Check An Explicit State
```csharp
if (!validated) throw new InvalidOperationException("Payment must be validated.");
```

## Checklist

- [ ] Preconditions validate all inputs and state
- [ ] Only store old values that can change
- [ ] Postconditions verify real effects
- [ ] Invariants are always enforced
- [ ] Error messages are actionable
