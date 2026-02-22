# uContract Guide (.NET)

## Purpose

`uContract` provides a lightweight API for Design by Contract.  
In .NET, the API must be preserved even if implemented locally.

## Core API (Expected in .NET)

```csharp
Contract.Require(condition, "message");
Contract.RequireNotNull("name", value);
Contract.Ensure(condition, "message");
Contract.Invariant(condition, "message");
Contract.Old(() => value);
Contract.EnsureAssignable(current, oldSnapshot, params string[] fields);
Contract.EnsureResult(result, predicate);
Contract.EnsureImmutableCollection(collection);
Contract.Reject("reason", predicate);
Contract.Check("message", predicate);
```

## Examples

### Precondition + Postcondition
```csharp
public void Rename(string newName)
{
    Contract.RequireNotNull("newName", newName);
    Contract.Require(!string.IsNullOrWhiteSpace(newName), "Name required");

    var oldName = Contract.Old(() => Name);
    Name = newName.Trim();

    Contract.Ensure(Name != oldName, "Name changed");
}
```

### EnsureAssignable
```csharp
var oldUser = Contract.Old(() => this.Clone());
Email = newEmail;
LastModified = DateProvider.Now();
Contract.EnsureAssignable(this, oldUser, "Email", "LastModified");
```

### EnsureResult
```csharp
return Contract.EnsureResult(user, u => u != null && u.IsActive);
```

## Performance Notes

- Prefer contract checks for core domain logic.
- Avoid heavy checks in hot paths if not needed.
- Consider conditional enabling in production (TODO).
