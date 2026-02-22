# Contract Design Examples (.NET)

This folder contains Design by Contract (DbC) guidance and examples.
The original implementation uses uContract. In .NET, the same
concepts must be preserved even if the library is reimplemented.

## Contents

- `CONTRACT-GUIDE.md` - DbC fundamentals
- `UCONTRACT-GUIDE.md` - Advanced uContract API usage
- `ucontract-detailed-examples.md` - Detailed API examples
- `aggregate-contract-example.md` - Aggregate contract examples
- `usecase-contract-example.md` - Use case contract examples
- `value-object-contract-example.md` - Value object contract examples

## Core Concepts

### Preconditions
```csharp
Contract.Require(amount > 0, "Amount must be positive");
Contract.RequireNotNull("account", account);
```

### Postconditions
```csharp
var oldBalance = Contract.Old(() => balance);
balance -= amount;
Contract.Ensure(balance < oldBalance, "Balance decreased");
```

### Invariants
```csharp
protected override void EnsureInvariant()
{
    Contract.Invariant(!Name.IsBlank(), "Name must not be blank");
}
```

## Library Note

`uContract` does not exist in .NET yet.  
Preserve the API and behavior in a .NET port (TODO).
