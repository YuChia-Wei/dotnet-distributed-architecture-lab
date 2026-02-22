# Aggregate Contract Example (.NET)

## Constructor Contract
```csharp
public Tag(TagId tagId, PlanId planId, string name, string color)
{
    Contract.RequireNotNull("tagId", tagId);
    Contract.RequireNotNull("planId", planId);
    Contract.RequireNotNull("name", name);
    Contract.RequireNotNull("color", color);
    Contract.Require(!string.IsNullOrWhiteSpace(name), "Name required");
    Contract.Require(IsValidHexColor(color), "Color must be HEX");

    Apply(new TagEvents.TagCreated(
        tagId, planId, name.Trim(), color.ToUpperInvariant(),
        Guid.NewGuid(), DateProvider.Now()));

    Contract.Ensure(Id == tagId, "Tag id set");
    Contract.Ensure(PlanId == planId, "Plan id set");
    Contract.Ensure(Name == name.Trim(), "Name set");
    Contract.Ensure(Color == color.ToUpperInvariant(), "Color set");
    Contract.Ensure(!IsDeleted, "Not deleted");
    Contract.Ensure(DomainEvents.Count == 1, "One event emitted");
}
```

## Rename Command
```csharp
public void Rename(string newName)
{
    Contract.RequireNotNull("newName", newName);
    Contract.Require(!string.IsNullOrWhiteSpace(newName), "Name required");
    Contract.Require(!IsDeleted, "Not deleted");

    var oldName = Name;
    var oldVersion = Version;
    var oldCount = DomainEvents.Count;

    if (Contract.Reject("Name unchanged", () => Name == newName.Trim()))
    {
        return;
    }

    Apply(new TagEvents.TagRenamed(
        Id, newName.Trim(), Guid.NewGuid(), DateProvider.Now()));

    Contract.Ensure(Name != oldName, "Name changed");
    Contract.Ensure(DomainEvents.Count == oldCount + 1, "Event emitted");
    Contract.Ensure(Version == oldVersion + 1, "Version incremented");
}
```

## Delete Command
```csharp
public void Delete()
{
    Contract.Require(!IsDeleted, "Not already deleted");

    var oldVersion = Version;
    var oldCount = DomainEvents.Count;

    Apply(new TagEvents.TagDeleted(Id, Guid.NewGuid(), DateProvider.Now()));

    Contract.Ensure(IsDeleted, "Marked deleted");
    Contract.Ensure(DomainEvents.Count == oldCount + 1, "Event emitted");
    Contract.Ensure(Version == oldVersion + 1, "Version incremented");
}
```

## Invariants
```csharp
protected override void EnsureInvariant()
{
    Contract.InvariantNotNull("tagId", Id);
    Contract.InvariantNotNull("planId", PlanId);
    Contract.InvariantNotNull("name", Name);
    Contract.InvariantNotNull("color", Color);
    Contract.Invariant(!string.IsNullOrWhiteSpace(Name), "Name required");
    Contract.Invariant(IsValidHexColor(Color), "Valid color");
}
```
