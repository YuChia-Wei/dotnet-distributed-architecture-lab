# Projection Patterns (.NET)

Projections implement the CQRS read side, optimized for specific queries.

## Structure

```
projection/
├── README.md
├── ProjectionDtos.cs
├── ProjectionModels.cs
├── ReadModelDbContext.cs
├── PlanDtosProjection.cs
├── EfPlanDtosProjection.cs
├── TasksByDateProjection.cs
├── EfTasksByDateProjection.cs
├── TasksDueTodayProjection.cs
├── EfTasksDueTodayProjection.cs
├── TasksSortedByDeadlineProjection.cs
├── AllTagsProjection.cs
└── EfAllTagsProjection.cs
```

## Key Rule (Do Not Skip)

Every projection must have:
1. **Interface** (contract)
2. **EF Core implementation**

Do not ship only the interface.

## Interface Pattern

```csharp
public interface IPlanDtosProjection
{
    IReadOnlyList<PlanDto> Query(PlanDtosProjectionInput input);
}
```

## EF Core Implementation Pattern

```csharp
public sealed class EfPlanDtosProjection : IPlanDtosProjection
{
    private readonly ReadModelDbContext _db;

    public IReadOnlyList<PlanDto> Query(PlanDtosProjectionInput input)
    {
        return _db.Plans
            .AsNoTracking()
            .Where(p => p.UserId == input.UserId && !p.IsDeleted)
            .OrderBy(p => p.Name)
            .Select(ReadModelMapper.ToPlanDto)
            .ToList();
    }
}
```

## Projection vs Repository

| Use Repository | Use Projection |
|---------------|----------------|
| Single aggregate lookup | Cross-aggregate queries |
| Full domain model | DTO-only read |
| Simple CRUD | Complex filtering |
| Writes involved | Read-only |

## Checklist

- [ ] Interface created
- [ ] EF Core implementation created
- [ ] Input model defined
- [ ] Mapper usage verified
- [ ] Query tested (in-memory or test DB)

## Related Resources
- `../usecase/README.md`
- `../mapper/README.md`
