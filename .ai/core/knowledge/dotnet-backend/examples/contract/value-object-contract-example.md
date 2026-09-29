# Value Object Contract Example (.NET)

## Immutability
Value Objects should be immutable and validated on creation.

```csharp
public sealed record ProjectName
{
    public string Value { get; }

    public ProjectName(string value)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(value);

        var normalized = value.Trim();
        if (normalized.Length > 100)
        {
            throw new ArgumentOutOfRangeException(
                nameof(value),
                "Name must not exceed 100 characters.");
        }

        Value = normalized;
    }
}
```

## Equality
Record types provide value-based equality by default.
If using classes, override `Equals` and `GetHashCode`.

## Invariants
Any invariant must be validated at construction time.
