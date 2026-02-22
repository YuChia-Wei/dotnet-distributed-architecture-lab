using System;
using System.Collections.Generic;
using System.Linq;
using Example.Plans.Domain;

namespace Example.Plans.UseCases.Port;

public static class PlanMapper
{
    public static PlanData ToData(Plan plan)
    {
        ArgumentNullException.ThrowIfNull(plan);

        var planData = new PlanData(plan.Version);
        planData.PlanId = plan.Id.Value;
        planData.Name = plan.Name;
        planData.UserId = plan.UserId;
        planData.NextTaskId = 0; // TODO: expose nextTaskId if needed
        planData.IsDeleted = plan.IsDeleted;

        if (plan.DomainEvents.Count > 0)
        {
            planData.CreatedAt = plan.DomainEvents[0].OccurredOn;
            planData.LastUpdated = plan.DomainEvents[^1].OccurredOn;
        }
        else
        {
            planData.CreatedAt = DateProvider.Now();
            planData.LastUpdated = DateProvider.Now();
        }

        planData.StreamName = plan.StreamName;
        planData.DomainEventDatas = plan.DomainEvents
            .Select(DomainEventMapper.ToData)
            .ToList();

        // Sync projects
        planData.ProjectDatas.RemoveAll(projectData =>
            !plan.GetProjects().ContainsKey(ProjectId.ValueOf(projectData.ProjectId)));

        foreach (var project in plan.GetProjects().Values)
        {
            var existing = planData.ProjectDatas
                .FirstOrDefault(pd => pd.ProjectId == project.Id.Value);

            if (existing == null)
            {
                planData.ProjectDatas.Add(ProjectMapper.ToData(project));
                continue;
            }

            existing.TaskDatas.RemoveAll(taskData =>
                !project.GetTasks().ContainsKey(TaskId.ValueOf(taskData.TaskId)));

            foreach (var task in project.GetTasks().Values)
            {
                var existingTask = existing.TaskDatas
                    .FirstOrDefault(td => td.TaskId == task.Id.Value);

                if (existingTask == null)
                {
                    existing.TaskDatas.Add(TaskMapper.ToData(task, project.Id.Value));
                    continue;
                }

                existingTask.Name = task.Name;
                existingTask.IsDone = task.IsDone;
                existingTask.TagIds = task.Tags.Select(tag => tag.Value).ToHashSet();
            }
        }

        return planData;
    }

    public static List<PlanData> ToData(IEnumerable<Plan> plans) =>
        plans.Select(ToData).ToList();

    public static PlanDto ToDto(Plan plan)
    {
        ArgumentNullException.ThrowIfNull(plan);

        var dto = new PlanDto()
            .SetId(plan.Id.Value)
            .SetName(plan.Name)
            .SetUserId(plan.UserId);

        dto.SetProjects(plan.GetProjects().Values.Select(ProjectMapper.ToDto));
        return dto;
    }

    public static Plan ToDomain(PlanData planData)
    {
        ArgumentNullException.ThrowIfNull(planData);

        if (planData.DomainEventDatas?.Count > 0)
        {
            var domainEvents = planData.DomainEventDatas
                .Select(DomainEventMapper.ToDomain)
                .Cast<PlanEvents.IPlanEvent>()
                .ToList();

            var plan = new Plan(domainEvents);
            plan.Version = planData.Version;
            plan.ClearDomainEvents();
            return plan;
        }

        var events = new List<PlanEvents.IPlanEvent>
        {
            new PlanEvents.PlanCreated(
                PlanId.ValueOf(planData.PlanId),
                planData.Name,
                planData.UserId,
                new Dictionary<string, string>(),
                Guid.NewGuid(),
                planData.CreatedAt
            )
        };

        foreach (var projectData in planData.ProjectDatas)
        {
            events.Add(new PlanEvents.ProjectCreated(
                PlanId.ValueOf(planData.PlanId),
                ProjectId.ValueOf(projectData.ProjectId),
                ProjectName.ValueOf(projectData.Name),
                new Dictionary<string, string>(),
                Guid.NewGuid(),
                planData.CreatedAt
            ));

            foreach (var taskData in projectData.TaskDatas)
            {
                events.Add(new PlanEvents.TaskCreated(
                    PlanId.ValueOf(planData.PlanId),
                    ProjectId.ValueOf(projectData.ProjectId),
                    ProjectName.ValueOf(projectData.Name),
                    TaskId.ValueOf(taskData.TaskId),
                    taskData.Name,
                    new Dictionary<string, string>(),
                    Guid.NewGuid(),
                    planData.CreatedAt
                ));

                if (taskData.IsDone)
                {
                    events.Add(new PlanEvents.TaskChecked(
                        PlanId.ValueOf(planData.PlanId),
                        ProjectId.ValueOf(projectData.ProjectId),
                        TaskId.ValueOf(taskData.TaskId),
                        new Dictionary<string, string>(),
                        Guid.NewGuid(),
                        planData.LastUpdated
                    ));
                }

                if (taskData.Deadline != null)
                {
                    events.Add(new PlanEvents.TaskDeadlineSet(
                        PlanId.ValueOf(planData.PlanId),
                        ProjectId.ValueOf(projectData.ProjectId),
                        TaskId.ValueOf(taskData.TaskId),
                        taskData.Deadline,
                        new Dictionary<string, string>(),
                        Guid.NewGuid(),
                        planData.LastUpdated
                    ));
                }

                foreach (var tagId in taskData.TagIds)
                {
                    events.Add(new PlanEvents.TagAssigned(
                        PlanId.ValueOf(planData.PlanId),
                        ProjectId.ValueOf(projectData.ProjectId),
                        TaskId.ValueOf(taskData.TaskId),
                        Example.Tags.Domain.TagId.ValueOf(tagId),
                        new Dictionary<string, string>(),
                        Guid.NewGuid(),
                        planData.LastUpdated
                    ));
                }
            }
        }

        if (planData.IsDeleted)
        {
            events.Add(new PlanEvents.PlanDeleted(
                PlanId.ValueOf(planData.PlanId),
                new Dictionary<string, string>(),
                Guid.NewGuid(),
                planData.LastUpdated
            ));
        }

        var rebuilt = new Plan(events);
        rebuilt.Version = planData.Version;
        rebuilt.ClearDomainEvents();
        return rebuilt;
    }

    public static List<Plan> ToDomain(IEnumerable<PlanData> planDatas) =>
        planDatas.Select(ToDomain).ToList();

    public static PlanDto ToDto(PlanData planData)
    {
        ArgumentNullException.ThrowIfNull(planData);

        var dto = new PlanDto()
            .SetId(planData.PlanId)
            .SetName(planData.Name)
            .SetUserId(planData.UserId);

        dto.SetProjects(planData.ProjectDatas.Select(ProjectMapper.ToDto));
        return dto;
    }

    public static List<PlanDto> ToDto(IEnumerable<PlanData> planDatas) =>
        planDatas.Select(ToDto).ToList();

    // Aggregate mappers expose an Outbox mapper.
    private static readonly IOutboxMapper<Plan, PlanData> Mapper = new MapperImpl();

    public static IOutboxMapper<Plan, PlanData> NewMapper() => Mapper;

    private sealed class MapperImpl : IOutboxMapper<Plan, PlanData>
    {
        public Plan ToDomain(PlanData data) => PlanMapper.ToDomain(data);
        public PlanData ToData(Plan aggregateRoot) => PlanMapper.ToData(aggregateRoot);
    }
}

// TODO: Replace placeholders below with EzDdd/Wolverine EF Core equivalents.
public interface IOutboxMapper<TAggregate, TData>
{
    TAggregate ToDomain(TData data);
    TData ToData(TAggregate aggregateRoot);
}

public static class DomainEventMapper
{
    public static DomainEventData ToData(object domainEvent) => new();
    public static object ToDomain(DomainEventData data) => new();
}

public sealed class DomainEventData { }

public sealed class PlanData
{
    public PlanData(int version) => Version = version;

    public int Version { get; set; }
    public string PlanId { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string UserId { get; set; } = string.Empty;
    public int NextTaskId { get; set; }
    public bool IsDeleted { get; set; }
    public DateTimeOffset CreatedAt { get; set; }
    public DateTimeOffset LastUpdated { get; set; }
    public string StreamName { get; set; } = string.Empty;
    public List<DomainEventData> DomainEventDatas { get; set; } = new();
    public List<ProjectData> ProjectDatas { get; set; } = new();
}

public sealed class ProjectData
{
    public string ProjectId { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public List<TaskData> TaskDatas { get; set; } = new();
}

public sealed class TaskData
{
    public string TaskId { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public bool IsDone { get; set; }
    public string? Deadline { get; set; }
    public HashSet<string> TagIds { get; set; } = new();
}
