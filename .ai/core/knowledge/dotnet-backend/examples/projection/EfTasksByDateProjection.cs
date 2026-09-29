using System.Collections.Generic;
using System.Linq;
using Microsoft.EntityFrameworkCore;

namespace Example.Plans.ReadModel;

public sealed class EfTasksByDateProjection : ITasksByDateProjection
{
    private readonly ReadModelDbContext _db;

    public EfTasksByDateProjection(ReadModelDbContext db)
    {
        _db = db;
    }

    public IReadOnlyList<TaskDueTodayDto> Query(TasksByDateProjectionInput input)
    {
        return _db.Plans
            .AsNoTracking()
            .Include(plan => plan.Projects)
            .ThenInclude(project => project.Tasks)
            .Where(plan => plan.UserId == input.UserId && !plan.IsDeleted)
            .SelectMany(plan => plan.Projects.SelectMany(project =>
                project.Tasks
                    .Where(task => task.Deadline == input.TargetDate)
                    .Select(task => ReadModelMapper.ToTaskDueTodayDto(plan, project, task))
            ))
            .OrderBy(dto => dto.PlanName)
            .ThenBy(dto => dto.ProjectName)
            .ThenBy(dto => dto.TaskId)
            .ToList();
    }
}
