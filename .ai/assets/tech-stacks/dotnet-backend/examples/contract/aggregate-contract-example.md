# Aggregate Contract Example (.NET)

This example uses standard .NET exceptions so the contract semantics remain
usable without selecting a helper package. A target may replace the guards with
an explicitly selected equivalent while preserving the same behavior.

## Constructor Contract
```csharp
public Tag(TagId tagId, PlanId planId, string name, string color)
{
    ArgumentNullException.ThrowIfNull(tagId);
    ArgumentNullException.ThrowIfNull(planId);
    ArgumentException.ThrowIfNullOrWhiteSpace(name);
    ArgumentException.ThrowIfNullOrWhiteSpace(color);
    if (!IsValidHexColor(color))
    {
        throw new ArgumentException("Color must be HEX.", nameof(color));
    }

    Apply(new TagEvents.TagCreated(
        tagId, planId, name.Trim(), color.ToUpperInvariant(),
        Guid.NewGuid(), DateProvider.Now()));

    EnsureInvariant();
}
```

Focused Domain tests should prove that construction sets the supplied identity,
normalizes name and color, leaves the Aggregate active, and emits one creation
event.

## Rename Command
```csharp
public void Rename(string newName)
{
    ArgumentException.ThrowIfNullOrWhiteSpace(newName);
    if (IsDeleted)
    {
        throw new InvalidOperationException("A deleted tag cannot be renamed.");
    }

    var normalizedName = newName.Trim();

    if (Name == normalizedName)
    {
        return;
    }

    Apply(new TagEvents.TagRenamed(
        Id, normalizedName, Guid.NewGuid(), DateProvider.Now()));

    EnsureInvariant();
}
```

Focused Domain tests should prove that a real rename changes the name, appends
one event, and increments the Aggregate version, while an identical normalized
name is a no-op.

## Delete Command
```csharp
public void Delete()
{
    if (IsDeleted)
    {
        throw new InvalidOperationException("The tag is already deleted.");
    }

    Apply(new TagEvents.TagDeleted(Id, Guid.NewGuid(), DateProvider.Now()));

    EnsureInvariant();
}
```

Focused Domain tests should prove the deleted state, emitted event, and version
increment.

## Invariants
```csharp
private void EnsureInvariant()
{
    if (Id is null || PlanId is null)
    {
        throw new InvalidOperationException("Tag identity is incomplete.");
    }

    if (string.IsNullOrWhiteSpace(Name) || !IsValidHexColor(Color))
    {
        throw new InvalidOperationException("Tag state violates its invariant.");
    }
}
```
