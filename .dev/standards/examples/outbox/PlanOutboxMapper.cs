using System;
using System.Collections.Generic;
using System.Linq;
using Example.Plans.Domain;
using Example.Plans.UseCases.Port;
using Example.Shared.Outbox;

namespace Example.Plans.Outbox;

public static class PlanOutboxMapper
{
    public static PlanData ToData(Plan plan)
    {
        ArgumentNullException.ThrowIfNull(plan);

        var planData = new PlanData
        {
            PlanId = plan.Id.Value,
            Name = plan.Name,
            UserId = plan.UserId,
            NextTaskId = 0,
            IsDeleted = plan.IsDeleted
        };

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

        planData.ProjectDatas.RemoveAll(projectData =>
            !plan.GetProjects().ContainsKey(ProjectId.ValueOf(projectData.ProjectId)));

        foreach (var project in plan.GetProjects().Values)
        {
            var existingProject = planData.ProjectDatas.FirstOrDefault(pd => pd.ProjectId == project.Id.Value);
            if (existingProject == null)
            {
                planData.AddProjectData(ProjectOutboxMapper.ToData(project));
                continue;
            }

            existingProject.TaskDatas.RemoveAll(taskData =>
                !project.GetTasks().ContainsKey(TaskId.ValueOf(taskData.TaskId)));

            foreach (var task in project.GetTasks().Values)
            {
                var existingTask = existingProject.TaskDatas.FirstOrDefault(td => td.TaskId == task.Id.Value);
                if (existingTask == null)
                {
                    existingProject.AddTaskData(TaskOutboxMapper.ToData(task, project.Id.Value));
                }
                else
                {
                    existingTask.Name = task.Name;
                    existingTask.IsDone = task.IsDone;
                    existingTask.TagIds = task.Tags.Select(tag => new TaskTagData
                    {
                        TaskId = task.Id.Value,
                        TagId = tag.Value
                    }).ToList();
                }
            }
        }

        return planData;
    }

    public static PlanDto ToDto(Plan plan)
    {
        ArgumentNullException.ThrowIfNull(plan);

        var dto = new PlanDto()
            .SetId(plan.Id.Value)
            .SetName(plan.Name)
            .SetUserId(plan.UserId);

        dto.SetProjects(plan.GetProjects().Values.Select(ProjectOutboxMapper.ToDto));
        return dto;
    }

    public static Plan ToDomain(PlanData planData)
    {
        ArgumentNullException.ThrowIfNull(planData);

        if (planData.DomainEventDatas is { Count: > 0 })
        {
            var events = planData.DomainEventDatas
                .Select(DomainEventMapper.ToDomain)
                .Cast<PlanEvents.IPlanEvent>()
                .ToList();
            var plan = new Plan(events) { Version = (int)planData.Version };
            plan.ClearDomainEvents();
            return plan;
        }

        // TODO: Rebuild events from data if no domain events are persisted.
        var reconstructed = new Plan(PlanId.ValueOf(planData.PlanId), planData.Name, planData.UserId)
        {
            Version = (int)planData.Version
        };
        reconstructed.ClearDomainEvents();
        return reconstructed;
    }

    private static readonly IOutboxMapper<Plan, PlanData> Mapper = new MapperImpl();

    public static IOutboxMapper<Plan, PlanData> NewMapper() => Mapper;

    private sealed class MapperImpl : IOutboxMapper<Plan, PlanData>
    {
        public Plan ToDomain(PlanData data) => PlanOutboxMapper.ToDomain(data);
        public PlanData ToData(Plan aggregateRoot) => PlanOutboxMapper.ToData(aggregateRoot);
    }
}

// TODO: Replace these placeholders with ezDDD .NET ports.
public interface IOutboxMapper<TAggregate, TData>
{
    TAggregate ToDomain(TData data);
    TData ToData(TAggregate aggregateRoot);
}

public static class DateProvider
{
    public static DateTimeOffset Now() => DateTimeOffset.UtcNow;
}
