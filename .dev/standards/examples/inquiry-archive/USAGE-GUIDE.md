# Inquiry and Archive Usage Guide (.NET)

## Inquiry

### 1) Define an Inquiry

```csharp
public interface IFindPbisBySprintIdInquiry
{
    IReadOnlyList<string> FindBySprintId(SprintId sprintId);
}
```

### 2) Implement with EF Core

```csharp
public sealed class EfFindPbisBySprintIdInquiry : IFindPbisBySprintIdInquiry
{
    private readonly ReadDbContext _db;

    public IReadOnlyList<string> FindBySprintId(SprintId sprintId)
        => _db.Pbis.Where(p => p.SprintId == sprintId.Value && !p.Deleted)
                  .OrderBy(p => p.OrderId)
                  .Select(p => p.PbiId)
                  .ToList();
}
```

### 3) Use in a Reactor

```csharp
public sealed class NotifyPbiWhenSprintStartedService : IWhenSprintStartedNotifyPbiReactor
{
    private readonly IFindPbisBySprintIdInquiry _inquiry;
    private readonly IStartPbiUseCase _useCase;

    public void Handle(DomainEventData message)
    {
        if (message == null) return;

        var domainEvent = DomainEventMapper.ToDomain(message);
        if (domainEvent is SprintStarted started)
        {
            var pbiIds = _inquiry.FindBySprintId(SprintId.ValueOf(started.SprintId));
            foreach (var pbiId in pbiIds)
            {
                _useCase.Execute(new StartPbiInput { PbiId = pbiId });
            }
        }
    }
}
```

## Archive

### 1) Define Archive Interface

```csharp
public interface IProductArchive
{
    void Archive(Product product, string reason, string archivedBy);
    ArchivedProduct? FindArchivedById(ProductId productId);
}
```

### 2) Define Archived Data

```csharp
public sealed record ArchivedProduct(
    string ProductId,
    string Name,
    string Goal,
    DateTimeOffset ArchivedAt,
    string ArchivedBy,
    string Reason,
    string OriginalDataJson
);
```

### 3) Implement Archive with EF Core

```csharp
public sealed class EfProductArchive : IProductArchive
{
    private readonly ReadDbContext _db;

    public void Archive(Product product, string reason, string archivedBy)
    {
        // TODO: serialize full aggregate state as JSON
        var archived = new ArchivedProduct(...);
        _db.ArchivedProducts.Add(archived);
        _db.SaveChanges();
    }
}
```

## Checklist

- [ ] Inquiry names follow `Find[What]By[Condition]Inquiry`
- [ ] Each inquiry handles one query only
- [ ] Archive stores metadata (who/when/why)
- [ ] Soft delete or archived tables are indexed
