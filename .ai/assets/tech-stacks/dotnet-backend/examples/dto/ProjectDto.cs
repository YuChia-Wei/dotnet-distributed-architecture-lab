using System.Collections.Generic;
using System.Linq;

namespace Example.Plans.UseCases.Port;

// Nested DTO template: parent-child relationships and derived counts.
public sealed class ProjectDto
{
    private readonly List<TaskDto> _tasks = new();

    public string Id { get; private set; } = string.Empty;
    public string Name { get; private set; } = string.Empty;
    public string PlanId { get; private set; } = string.Empty;
    public IReadOnlyList<TaskDto> Tasks => _tasks;

    public int CompletedTaskCount { get; private set; }
    public int TotalTaskCount { get; private set; }

    public ProjectDto()
    {
        CompletedTaskCount = 0;
        TotalTaskCount = 0;
    }

    public ProjectDto(string id, string name) : this()
    {
        Id = id;
        Name = name;
    }

    public ProjectDto SetId(string id)
    {
        Id = id;
        return this;
    }

    public ProjectDto SetName(string name)
    {
        Name = name;
        return this;
    }

    public ProjectDto SetPlanId(string planId)
    {
        PlanId = planId;
        return this;
    }

    public ProjectDto SetTasks(IEnumerable<TaskDto> tasks)
    {
        _tasks.Clear();
        _tasks.AddRange(tasks);
        UpdateTaskCounts();
        return this;
    }

    public ProjectDto SetCompletedTaskCount(int completedTaskCount)
    {
        CompletedTaskCount = completedTaskCount;
        return this;
    }

    public ProjectDto SetTotalTaskCount(int totalTaskCount)
    {
        TotalTaskCount = totalTaskCount;
        return this;
    }

    public ProjectDto AddTask(TaskDto task)
    {
        _tasks.Add(task);
        TotalTaskCount++;
        if (task.IsDone)
        {
            CompletedTaskCount++;
        }
        return this;
    }

    public ProjectDto RemoveTask(string taskId)
    {
        var removed = _tasks.RemoveAll(task => task.Id == taskId);
        if (removed > 0)
        {
            TotalTaskCount -= removed;
            CompletedTaskCount = _tasks.Count(task => task.IsDone);
        }
        return this;
    }

    private void UpdateTaskCounts()
    {
        TotalTaskCount = _tasks.Count;
        CompletedTaskCount = _tasks.Count(task => task.IsDone);
    }
}
