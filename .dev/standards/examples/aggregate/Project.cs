using System;
using System.Collections.Generic;
using Example.Tags.Domain;

namespace Example.Plans.Domain;

public sealed class Project : IEntity<ProjectId>
{
    private readonly Dictionary<TaskId, Task> _tasks = new();

    public Project(ProjectId id, ProjectName name, PlanId planId)
    {
        ArgumentNullException.ThrowIfNull(id);
        ArgumentNullException.ThrowIfNull(name);
        ArgumentNullException.ThrowIfNull(planId);

        Id = id;
        Name = name;
        PlanId = planId;
    }

    public ProjectId Id { get; }
    public ProjectName Name { get; }
    public PlanId PlanId { get; }

    public void CreateTask(TaskId taskId, string taskName)
    {
        if (string.IsNullOrWhiteSpace(taskName))
        {
            throw new ArgumentException("Task name cannot be empty.", nameof(taskName));
        }

        var task = new Task(taskId, taskName, Name);
        _tasks[taskId] = task;
    }

    public bool HasTask(TaskId taskId) => _tasks.ContainsKey(taskId);

    public Task? GetTask(TaskId taskId) => _tasks.TryGetValue(taskId, out var task) ? task : null;

    public void CheckTask(TaskId taskId)
    {
        if (_tasks.TryGetValue(taskId, out var task))
        {
            task.MarkAsDone();
        }
    }

    public void UncheckTask(TaskId taskId)
    {
        if (_tasks.TryGetValue(taskId, out var task))
        {
            task.UnmarkAsDone();
        }
    }

    public void DeleteTask(TaskId taskId) => _tasks.Remove(taskId);

    public void SetTaskDeadline(TaskId taskId, DateOnly? deadline)
    {
        if (_tasks.TryGetValue(taskId, out var task))
        {
            task.SetDeadline(deadline);
        }
    }

    public void RenameTask(TaskId taskId, string newName)
    {
        if (_tasks.TryGetValue(taskId, out var task))
        {
            task.Rename(newName);
        }
    }

    internal void AddTask(Task task) => _tasks[task.Id] = task;

    public IReadOnlyDictionary<TaskId, Task> GetTasks() => new Dictionary<TaskId, Task>(_tasks);

    public override bool Equals(object? obj) =>
        obj is Project other && Equals(Id, other.Id);

    public override int GetHashCode() => Id.GetHashCode();
}

// NOTE: Task is co-located to keep the example compact (legacy sample omits Task).
public sealed class Task
{
    private readonly HashSet<TagId> _tags = new();

    public Task(TaskId id, string name, ProjectName projectName)
    {
        ArgumentNullException.ThrowIfNull(id);
        ArgumentNullException.ThrowIfNull(projectName);
        if (string.IsNullOrWhiteSpace(name))
        {
            throw new ArgumentException("Task name cannot be empty.", nameof(name));
        }

        Id = id;
        Name = name;
        ProjectName = projectName;
    }

    public TaskId Id { get; }
    public string Name { get; private set; }
    public ProjectName ProjectName { get; }
    public bool IsDone { get; private set; }
    public DateOnly? Deadline { get; private set; }

    public IEnumerable<TagId> Tags => _tags;

    public void MarkAsDone() => IsDone = true;
    public void UnmarkAsDone() => IsDone = false;

    public void Rename(string newName)
    {
        if (string.IsNullOrWhiteSpace(newName))
        {
            throw new ArgumentException("Task name cannot be empty.", nameof(newName));
        }
        Name = newName;
    }

    public void SetDeadline(DateOnly? deadline) => Deadline = deadline;

    public bool HasTag(TagId tagId) => _tags.Contains(tagId);
    public void AssignTag(TagId tagId) => _tags.Add(tagId);
    public void UnassignTag(TagId tagId) => _tags.Remove(tagId);
}

// TODO: Replace with EzDdd.Entity<TId> when the .NET port is available.
public interface IEntity<out TId>
{
    TId Id { get; }
}
