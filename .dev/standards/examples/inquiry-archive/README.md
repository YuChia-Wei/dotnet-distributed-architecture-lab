# Inquiry and Archive Patterns (.NET)

In addition to Repository and Projection, the ezDDD CQRS architecture uses:
- **Inquiry**: targeted, read-only queries for complex conditions
- **Archive**: soft-delete and historical retention patterns

## Inquiry

Use Inquiry when:
- Cross-aggregate queries are required
- Reactors need read access to other aggregates
- Query logic is too specific for a projection

Do not use Inquiry for:
- Simple `FindById` (Repository)
- Standard list views (Projection)
- Data reachable via aggregate navigation

### Example (Interface)

```csharp
public interface IFindCardsByTagIdInquiry : IInquiry<TagId, IReadOnlyList<string>> { }
```

### Example (EF Core)

```csharp
public sealed class EfFindCardsByTagIdInquiry : IFindCardsByTagIdInquiry
{
    public IReadOnlyList<string> Query(TagId tagId) =>
        _db.Cards.Where(card => card.Tags.Any(tag => tag.TagId == tagId.Value))
                 .Select(card => card.CardId)
                 .ToList();
}
```

### Example (Event Store)

```csharp
public sealed class EsFindCardsByTagIdInquiry : IFindCardsByTagIdInquiry
{
    public IReadOnlyList<string> Query(TagId tagId) { /* scan events */ }
}
```

## Archive

Use Archive when:
- Soft-delete and audit retention are required
- Historical records must be preserved

Do not use Archive when:
- Data can be removed permanently
- Event sourcing already provides full history

### Example (Interface)

```csharp
public interface IUserArchive : IArchive<UserData, string> { }
```

### Example (EF Core)

```csharp
public sealed class EfUserArchive : IUserArchive
{
    public void Save(UserData entity) { /* persist */ }
}
```

## Inquiry vs Projection vs Archive

| Feature | Repository | Projection | Inquiry | Archive |
|---------|------------|------------|---------|---------|
| Purpose | CRUD | Read view | Complex query | Soft delete |
| Writes | Yes | No | No | Yes |
| Output | Aggregate | DTO | IDs/DTO | Archived DTO |

## Related Resources
- `../projection/README.md`
- `../usecase/README.md`
