using System;
using System.Linq;
using Example.Plans.Domain;
using Example.Plans.UseCases.Port;
using Example.Tags.Domain;

namespace Example.Plans.Outbox;

public static class TaskOutboxMapper
{
    public static TaskData ToData(Task task, string projectId)
    {
        ArgumentNullException.ThrowIfNull(task);
        ArgumentNullException.ThrowIfNull(projectId);

        var data = new TaskData
        {
            TaskId = task.Id.Value,
            Name = task.Name,
            ProjectName = task.ProjectName.Value,
            ProjectId = projectId,
            IsDone = task.IsDone,
            Deadline = task.Deadline
        };

        data.TagIds = task.Tags.Select(tag => new TaskTagData
        {
            TaskId = task.Id.Value,
            TagId = tag.Value
        }).ToList();

        return data;
    }

    public static TaskDto ToDto(Task task)
    {
        ArgumentNullException.ThrowIfNull(task);

        return new TaskDto()
            .SetId(task.Id.Value)
            .SetName(task.Name)
            .SetDone(task.IsDone)
            .SetDeadline(task.Deadline)
            .SetTagIds(task.Tags.Select(tag => tag.Value).ToList());
    }

    public static TaskDto ToDto(TaskData taskData)
    {
        ArgumentNullException.ThrowIfNull(taskData);

        var dto = new TaskDto()
            .SetId(taskData.TaskId)
            .SetName(taskData.Name)
            .SetDone(taskData.IsDone)
            .SetDeadline(taskData.Deadline);

        dto.SetTagIds(taskData.TagIds.Select(tag => tag.TagId).ToList());
        return dto;
    }

    public static Task ToDomain(TaskDto taskDto, ProjectName projectName)
    {
        ArgumentNullException.ThrowIfNull(taskDto);
        ArgumentNullException.ThrowIfNull(projectName);

        var task = new Task(TaskId.ValueOf(taskDto.Id), taskDto.Name, projectName);
        // TODO: apply tags and done status via domain methods.
        return task;
    }
}
