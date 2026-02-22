# Value Object Contract Example (.NET)

## Immutability
Value Objects should be immutable and validated on creation.

```csharp
public sealed record ProjectName
{
    public string Value { get; }

    public ProjectName(string value)
    {
        Contract.RequireNotNull("value", value);
        Contract.Require(!string.IsNullOrWhiteSpace(value), "Name required");
        Contract.Require(value.Length <= 100, "Name too long");
        Value = value.Trim();
    }
}
```

## Equality
Record types provide value-based equality by default.
If using classes, override `Equals` and `GetHashCode`.

## Invariants
Any invariant must be validated at construction time.
