using System;
using System.Collections.Generic;
using System.Linq;
using Example.Plans.Domain;
using Example.Tags.Domain;

namespace Example.Plans.UseCases.Port;

public static class TaskMapper
{
    public static TaskData ToData(Task task, string projectId)
    {
        ArgumentNullException.ThrowIfNull(task);
        ArgumentNullException.ThrowIfNull(projectId);

        var taskData = new TaskData
        {
            TaskId = task.Id.Value,
            Name = task.Name,
            IsDone = task.IsDone,
            Deadline = task.Deadline?.ToString("yyyy-MM-dd"),
            TagIds = task.Tags.Select(tag => tag.Value).ToHashSet()
        };

        // projectId is usually represented by the ProjectData relationship
        return taskData;
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
            .SetDone(taskData.IsDone);

        if (taskData.Deadline != null && DateOnly.TryParse(taskData.Deadline, out var deadline))
        {
            dto.SetDeadline(deadline);
        }

        dto.SetTagIds(taskData.TagIds);
        return dto;
    }

    public static Task ToDomain(TaskDto taskDto, ProjectName projectName)
    {
        ArgumentNullException.ThrowIfNull(taskDto);
        ArgumentNullException.ThrowIfNull(projectName);

        var task = new Task(TaskId.ValueOf(taskDto.Id), taskDto.Name, projectName);

        // TODO: map IsDone via domain methods if required (MarkAsDone/UnmarkAsDone).
        // TODO: map tags through domain methods to preserve invariants.

        return task;
    }
}
