# Contract Design Examples (.NET)

This folder contains Design by Contract (DbC) guidance and examples. The
examples preserve DbC semantics without selecting a package or prescribing a
shared helper API.

## Contents

- `CONTRACT-GUIDE.md` - DbC fundamentals
- `aggregate-contract-example.md` - Aggregate contract examples
- `usecase-contract-example.md` - Use case contract examples
- `value-object-contract-example.md` - Value object contract examples

## Core Concepts

### Preconditions
```csharp
ArgumentOutOfRangeException.ThrowIfNegativeOrZero(amount);
ArgumentNullException.ThrowIfNull(account);
```

### Postconditions
```csharp
var balanceBefore = balance;
balance -= amount;
if (balance >= balanceBefore)
{
    throw new InvalidOperationException("Balance must decrease.");
}
```

### Invariants
```csharp
private void EnsureInvariant()
{
    if (string.IsNullOrWhiteSpace(Name))
    {
        throw new InvalidOperationException("Name must not be blank.");
    }
}
```
