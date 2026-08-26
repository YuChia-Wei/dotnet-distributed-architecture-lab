using System;
using System.Linq;
using Example.Plans.Domain;
using Example.Plans.UseCases.Port;

namespace Example.Plans.Outbox;

public static class ProjectOutboxMapper
{
    public static ProjectData ToData(Project project)
    {
        ArgumentNullException.ThrowIfNull(project);

        var projectData = new ProjectData
        {
            ProjectId = project.Id.Value,
            Name = project.Name.Value
        };

        foreach (var task in project.GetTasks().Values)
        {
            projectData.AddTaskData(TaskOutboxMapper.ToData(task, project.Id.Value));
        }

        return projectData;
    }

    public static ProjectDto ToDto(Project project)
    {
        ArgumentNullException.ThrowIfNull(project);

        var dto = new ProjectDto()
            .SetId(project.Id.Value)
            .SetName(project.Name.Value);

        dto.SetTasks(project.GetTasks().Values.Select(TaskOutboxMapper.ToDto));
        return dto;
    }

    public static ProjectDto ToDto(ProjectData projectData)
    {
        ArgumentNullException.ThrowIfNull(projectData);

        var dto = new ProjectDto()
            .SetId(projectData.ProjectId)
            .SetName(projectData.Name);

        dto.SetTasks(projectData.TaskDatas.Select(TaskOutboxMapper.ToDto));
        return dto;
    }

    public static Project ToDomain(ProjectDto projectDto, PlanId planId)
    {
        ArgumentNullException.ThrowIfNull(projectDto);
        ArgumentNullException.ThrowIfNull(planId);

        return new Project(
            ProjectId.ValueOf(projectDto.Id),
            ProjectName.ValueOf(projectDto.Name),
            planId
        );
    }
}
