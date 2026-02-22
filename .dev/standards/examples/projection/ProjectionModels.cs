using System;
using System.Collections.Generic;
using System.Linq;
using Example.Plans.UseCases.Port;

namespace Example.Plans.ReadModel;

// TODO: Replace these read models with actual EF Core entities in your read-side project.
public sealed class PlanReadModel
{
    public string PlanId { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string UserId { get; set; } = string.Empty;
    public bool IsDeleted { get; set; }
    public DateTimeOffset LastUpdated { get; set; }
    public List<ProjectReadModel> Projects { get; set; } = new();
}

public sealed class ProjectReadModel
{
    public string ProjectId { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public List<TaskReadModel> Tasks { get; set; } = new();
}

public sealed class TaskReadModel
{
    public string TaskId { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public bool IsDone { get; set; }
    public DateOnly? Deadline { get; set; }
    public List<string> TagIds { get; set; } = new();
}

public sealed class TagReadModel
{
    public string TagId { get; set; } = string.Empty;
    public string PlanId { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string Color { get; set; } = string.Empty;
    public bool IsDeleted { get; set; }
}

public static class ReadModelMapper
{
    public static PlanDto ToPlanDto(PlanReadModel plan)
    {
        var dto = new PlanDto()
            .SetId(plan.PlanId)
            .SetName(plan.Name)
            .SetUserId(plan.UserId);

        dto.SetProjects(plan.Projects.Select(ToProjectDto));
        return dto;
    }

    private static ProjectDto ToProjectDto(ProjectReadModel project)
    {
        var dto = new ProjectDto(project.ProjectId, project.Name);
        dto.SetTasks(project.Tasks.Select(ToTaskDto));
        return dto;
    }

    private static TaskDto ToTaskDto(TaskReadModel task)
    {
        return new TaskDto()
            .SetId(task.TaskId)
            .SetName(task.Name)
            .SetDone(task.IsDone)
            .SetDeadline(task.Deadline);
    }

    public static TaskDueTodayDto ToTaskDueTodayDto(PlanReadModel plan, ProjectReadModel project, TaskReadModel task)
    {
        return new TaskDueTodayDto(
            task.TaskId,
            task.Name,
            task.IsDone,
            task.Deadline,
            plan.PlanId,
            plan.Name,
            project.Name
        );
    }

    public static TagDto ToTagDto(TagReadModel tag) => new(tag.TagId, tag.Name, tag.Color);
}
