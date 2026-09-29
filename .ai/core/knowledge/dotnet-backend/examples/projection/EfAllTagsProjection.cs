using System.Collections.Generic;
using System.Linq;
using Example.Plans.ReadModel;
using Microsoft.EntityFrameworkCore;

namespace Example.Tags.ReadModel;

public sealed class EfAllTagsProjection : IAllTagsProjection
{
    private readonly ReadModelDbContext _db;

    public EfAllTagsProjection(ReadModelDbContext db)
    {
        _db = db;
    }

    public IReadOnlyList<TagDto> Query(AllTagsProjectionInput input)
    {
        return _db.Tags
            .AsNoTracking()
            .Where(tag => tag.PlanId == input.PlanId && !tag.IsDeleted)
            .OrderBy(tag => tag.Name)
            .Select(ReadModelMapper.ToTagDto)
            .ToList();
    }
}
