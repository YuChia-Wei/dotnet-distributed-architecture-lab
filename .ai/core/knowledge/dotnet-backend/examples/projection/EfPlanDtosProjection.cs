using System.Collections.Generic;
using System.Linq;
using Microsoft.EntityFrameworkCore;

namespace Example.Plans.ReadModel;

public sealed class EfPlanDtosProjection : IPlanDtosProjection
{
    private readonly ReadModelDbContext _db;

    public EfPlanDtosProjection(ReadModelDbContext db)
    {
        _db = db;
    }

    public IReadOnlyList<Example.Plans.UseCases.Port.PlanDto> Query(PlanDtosProjectionInput input)
    {
        var query = _db.Plans
            .AsNoTracking()
            .Include(plan => plan.Projects)
            .ThenInclude(project => project.Tasks)
            .Where(plan => plan.UserId == input.UserId && !plan.IsDeleted);

        query = (input.SortBy, input.SortOrder) switch
        {
            (PlanSortBy.LastModified, PlanSortOrder.Desc) => query.OrderByDescending(plan => plan.LastUpdated),
            (PlanSortBy.LastModified, PlanSortOrder.Asc) => query.OrderBy(plan => plan.LastUpdated),
            (PlanSortBy.Name, PlanSortOrder.Desc) => query.OrderByDescending(plan => plan.Name),
            _ => query.OrderBy(plan => plan.Name)
        };

        return query
            .AsEnumerable()
            .Select(ReadModelMapper.ToPlanDto)
            .ToList();
    }
}
