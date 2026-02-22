# uContract Detailed Examples (.NET)

## old()
```csharp
var oldBalance = Contract.Old(() => Balance);
Balance += amount;
Contract.Ensure(Balance == oldBalance + amount, "Balance updated");
```

## ensureAssignable()
```csharp
var oldSnapshot = Contract.Old(() => Clone());
Status = Status.Closed;
ClosedAt = DateProvider.Now();
Contract.EnsureAssignable(this, oldSnapshot, "Status", "ClosedAt");
```

## ensureResult()
```csharp
return Contract.EnsureResult(result, r => r != null && r.IsSuccess);
```

## ensureImmutableCollection()
```csharp
public IReadOnlyList<Tag> Tags
    => Contract.EnsureImmutableCollection(_tags.AsReadOnly());
```

## reject()
```csharp
if (Contract.Reject("No change", () => Name == newName))
{
    return;
}
```

## check()
```csharp
Contract.Check("Payment validated", () => validated);
```

## requireNotNull()
```csharp
Contract.RequireNotNull("planId", planId);
```
