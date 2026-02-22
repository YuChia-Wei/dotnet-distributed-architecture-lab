using System;
using System.Collections.Generic;
using System.Linq;
using Microsoft.EntityFrameworkCore;

namespace Example.Plans.ReadModel;

public sealed class EfTasksDueTodayProjection : ITasksDueTodayProjection
{
    private readonly ReadModelDbContext _db;

    public EfTasksDueTodayProjection(ReadModelDbContext db)
    {
        _db = db;
    }

    public IReadOnlyList<TaskDueTodayDto> Query(TasksDueTodayProjectionInput input)
    {
        var today = DateOnly.FromDateTime(DateTime.UtcNow);

        return _db.Plans
            .AsNoTracking()
            .Include(plan => plan.Projects)
            .ThenInclude(project => project.Tasks)
            .Where(plan => plan.UserId == input.UserId && !plan.IsDeleted)
            .SelectMany(plan => plan.Projects.SelectMany(project =>
                project.Tasks
                    .Where(task => task.Deadline == today)
                    .Select(task => ReadModelMapper.ToTaskDueTodayDto(plan, project, task))
            ))
            .ToList();
    }
}
