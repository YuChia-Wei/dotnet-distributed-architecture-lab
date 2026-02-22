using System;
using System.Collections.Generic;
using System.Linq;
using Example.Tags.Domain;

namespace Example.Plans.Domain;

public sealed class Plan : EsAggregateRoot<PlanId, PlanEvents.IPlanEvent>
{
    public const string CategoryValue = "Plan";

    private PlanId _id = PlanId.ValueOf("unset");
    private string _name = string.Empty;
    private string _userId = string.Empty;
    private readonly Dictionary<ProjectId, Project> _projects = new();
    private int _nextTaskId;
    private bool _isDeleted;

    // Constructor for event sourcing framework to rebuild aggregate from events
    public Plan(IEnumerable<PlanEvents.IPlanEvent> domainEvents) : base(domainEvents)
    {
    }

    // Public constructor for creating new instances
    public Plan(PlanId planId, string name, string userId)
    {
        Contract.RequireNotNull("Plan id", planId);
        Contract.RequireNotNull("Plan name", name);
        Contract.RequireNotNull("User id", userId);

        Apply(new PlanEvents.PlanCreated(
            planId,
            name,
            userId,
            new Dictionary<string, string>(),
            Guid.NewGuid(),
            DateProvider.Now()
        ));

        Contract.Ensure($"Plan id is '{planId}'", () => Id.Equals(planId));
        Contract.Ensure($"Plan name is '{name}'", () => Name == name);
        Contract.Ensure($"User id is '{userId}'", () => UserId == userId);
        Contract.Ensure("A PlanCreated event is generated correctly", () =>
            LastDomainEvent is PlanEvents.PlanCreated created &&
            created.PlanId.Equals(planId) &&
            created.Name == name &&
            created.UserId == userId
        );
    }

    public override string Category => CategoryValue;
    public override PlanId Id => _id;
    public string Name => _name;
    public string UserId => _userId;
    public override bool IsDeleted => _isDeleted;

    public void Rename(string newName)
    {
        Contract.RequireNotNull("New name", newName);
        Contract.Require("New name not empty", () => !string.IsNullOrWhiteSpace(newName));
        Contract.Require("New name is different", () => !string.Equals(_name, newName, StringComparison.Ordinal));

        Apply(new PlanEvents.PlanRenamed(
            _id,
            newName,
            new Dictionary<string, string>(),
            Guid.NewGuid(),
            DateProvider.Now()
        ));

        Contract.Ensure($"Plan name is changed to '{newName}'", () => Name == newName);
        Contract.Ensure("A PlanRenamed event is generated correctly", () =>
            LastDomainEvent is PlanEvents.PlanRenamed renamed &&
            renamed.PlanId.Equals(_id) &&
            renamed.NewName == newName
        );
    }

    public void CreateProject(ProjectId projectId, ProjectName projectName)
    {
        Contract.RequireNotNull("Project id", projectId);
        Contract.RequireNotNull("Project name", projectName);
        Contract.Require("Project id must be unique", () => !HasProject(projectId));

        Apply(new PlanEvents.ProjectCreated(
            _id,
            projectId,
            projectName,
            new Dictionary<string, string>(),
            Guid.NewGuid(),
            DateProvider.Now()
        ));

        Contract.Ensure($"Project with id '{projectId}' exists", () => HasProject(projectId));
        Contract.Ensure($"Project name is '{projectName}'", () => GetProject(projectId)?.Name.Equals(projectName) == true);
    }

    public bool HasProject(ProjectId projectId) => _projects.ContainsKey(projectId);

    public Project? GetProject(ProjectId projectId) =>
        _projects.TryGetValue(projectId, out var project) ? project : null;

    public bool HasProject(ProjectName projectName) =>
        _projects.Values.Any(project => project.Name.Equals(projectName));

    public Project? GetProject(ProjectName projectName) =>
        _projects.Values.FirstOrDefault(project => project.Name.Equals(projectName));

    public IReadOnlyDictionary<ProjectId, Project> GetProjects() =>
        new Dictionary<ProjectId, Project>(_projects);

    public TaskId CreateTask(ProjectName projectName, TaskId taskId, string taskName)
    {
        Contract.RequireNotNull("Project name", projectName);
        Contract.RequireNotNull("Task name", taskName);
        Contract.Require("Task name not empty", () => !string.IsNullOrWhiteSpace(taskName));

        var project = GetProject(projectName);
        Contract.Require("Project must exist", () => project != null);

        project!.CreateTask(taskId, taskName);

        Apply(new PlanEvents.TaskCreated(
            _id,
            project.Id,
            project.Name,
            taskId,
            taskName,
            new Dictionary<string, string>(),
            Guid.NewGuid(),
            DateProvider.Now()
        ));

        Contract.Ensure($"Task with id '{taskId}' exists in project '{projectName}'", () => project.HasTask(taskId));
        Contract.Ensure($"Task name is '{taskName}'", () => project.GetTask(taskId)?.Name == taskName);

        return taskId;
    }

    public bool HasTask(TaskId taskId) =>
        _projects.Values.Any(project => project.HasTask(taskId));

    public Task? GetTask(TaskId taskId) =>
        _projects.Values.Select(project => project.GetTask(taskId)).FirstOrDefault(task => task != null);

    public void CheckTask(ProjectName projectName, TaskId taskId)
    {
        var project = GetProject(projectName);
        Contract.Require("Project must exist", () => project != null);
        Contract.Require("Task must exist in project", () => project!.HasTask(taskId));

        var task = project!.GetTask(taskId);
        Contract.Require("Task must not already be done", () => task != null && !task.IsDone);

        project.CheckTask(taskId);

        Apply(new PlanEvents.TaskChecked(
            _id,
            project.Id,
            taskId,
            new Dictionary<string, string>(),
            Guid.NewGuid(),
            DateProvider.Now()
        ));

        Contract.Ensure($"Task with id '{taskId}' is done", () => project.GetTask(taskId)?.IsDone == true);
    }

    public void UncheckTask(ProjectName projectName, TaskId taskId)
    {
        Contract.RequireNotNull("Project name", projectName);
        Contract.RequireNotNull("Task id", taskId);

        var project = GetProject(projectName);
        Contract.Require("Project must exist", () => project != null);
        Contract.Require("Task must exist in project", () => project!.HasTask(taskId));

        var task = project!.GetTask(taskId);
        Contract.Require("Task must be done", () => task != null && task.IsDone);

        project.UncheckTask(taskId);

        Apply(new PlanEvents.TaskUnchecked(
            _id,
            project.Id,
            taskId,
            new Dictionary<string, string>(),
            Guid.NewGuid(),
            DateProvider.Now()
        ));

        Contract.Ensure($"Task with id '{taskId}' is not done", () => project.GetTask(taskId)?.IsDone == false);
    }

    public void DeleteProject(ProjectId projectId)
    {
        Contract.RequireNotNull("Project id", projectId);
        Contract.Require("Plan must not be deleted", () => !_isDeleted);
        Contract.Require("Project must exist", () => HasProject(projectId));

        var project = GetProject(projectId);
        Contract.Require("Project must not have any tasks", () => project != null && !project.GetTasks().Any());

        Apply(new PlanEvents.ProjectDeleted(
            _id,
            projectId,
            new Dictionary<string, string>(),
            Guid.NewGuid(),
            DateProvider.Now()
        ));

        Contract.Ensure($"Project with id '{projectId}' is deleted", () => !HasProject(projectId));
    }

    public void DeleteTask(ProjectName projectName, TaskId taskId)
    {
        Contract.RequireNotNull("Project name", projectName);
        Contract.RequireNotNull("Task id", taskId);
        Contract.Require("Plan must not be deleted", () => !_isDeleted);
        Contract.Require("Project must exist", () => HasProject(projectName));

        var project = GetProject(projectName);
        Contract.Require("Task must exist in project", () => project != null && project.HasTask(taskId));

        project!.DeleteTask(taskId);

        Apply(new PlanEvents.TaskDeleted(
            _id,
            project.Id,
            taskId,
            new Dictionary<string, string>(),
            Guid.NewGuid(),
            DateProvider.Now()
        ));

        Contract.Ensure($"Task with id '{taskId}' is deleted from project '{projectName}'", () => !project.HasTask(taskId));
    }

    public void SetTaskDeadline(ProjectName projectName, TaskId taskId, DateOnly? deadline)
    {
        Contract.RequireNotNull("Project name", projectName);
        Contract.RequireNotNull("Task id", taskId);
        Contract.Require("Plan must not be deleted", () => !_isDeleted);
        Contract.Require("Project must exist", () => HasProject(projectName));

        var project = GetProject(projectName);
        Contract.Require("Task must exist in project", () => project != null && project.HasTask(taskId));

        project!.SetTaskDeadline(taskId, deadline);

        Apply(new PlanEvents.TaskDeadlineSet(
            _id,
            project.Id,
            taskId,
            deadline?.ToString("yyyy-MM-dd"),
            new Dictionary<string, string>(),
            Guid.NewGuid(),
            DateProvider.Now()
        ));

        Contract.Ensure($"Task deadline is set for task '{taskId}' in project '{projectName}'",
            () => project.GetTask(taskId)?.Deadline == deadline);
    }

    public void RenameTask(ProjectName projectName, TaskId taskId, string newName)
    {
        Contract.RequireNotNull("Project name", projectName);
        Contract.RequireNotNull("Task id", taskId);
        Contract.RequireNotNull("New task name", newName);
        Contract.Require("Plan must not be deleted", () => !_isDeleted);
        Contract.Require("Project must exist", () => HasProject(projectName));
        Contract.Require("New task name must not be empty", () => !string.IsNullOrWhiteSpace(newName));

        var project = GetProject(projectName);
        Contract.Require("Task must exist in project", () => project != null && project.HasTask(taskId));

        project!.RenameTask(taskId, newName);

        Apply(new PlanEvents.TaskRenamed(
            _id,
            project.Id,
            taskId,
            newName,
            new Dictionary<string, string>(),
            Guid.NewGuid(),
            DateProvider.Now()
        ));

        Contract.Ensure($"Task '{taskId}' is renamed to '{newName}' in project '{projectName}'",
            () => project.GetTask(taskId)?.Name == newName);
    }

    public void Delete()
    {
        Contract.Require("Plan must not already be deleted", () => !_isDeleted);

        Apply(new PlanEvents.PlanDeleted(
            _id,
            new Dictionary<string, string>(),
            Guid.NewGuid(),
            DateProvider.Now()
        ));

        Contract.Ensure("Plan is marked as deleted", () => _isDeleted);
    }

    public void AssignTag(ProjectId projectId, TaskId taskId, TagId tagId)
    {
        Contract.RequireNotNull("Project id", projectId);
        Contract.RequireNotNull("Task id", taskId);
        Contract.RequireNotNull("Tag id", tagId);
        Contract.Require("Plan is not deleted", () => !_isDeleted);
        Contract.Require("Project exists", () => HasProject(projectId));

        var project = GetProject(projectId);
        Contract.Require("Task exists in project", () => project != null && project.HasTask(taskId));

        var task = project!.GetTask(taskId);
        Contract.Require("Tag not already assigned", () => task != null && !task.HasTag(tagId));

        Apply(new PlanEvents.TagAssigned(
            _id,
            project.Id,
            taskId,
            tagId,
            new Dictionary<string, string>(),
            Guid.NewGuid(),
            DateProvider.Now()
        ));

        Contract.Ensure("Tag is assigned to task", () => task != null && task.HasTag(tagId));
    }

    public void UnassignTag(ProjectId projectId, TaskId taskId, TagId tagId)
    {
        Contract.RequireNotNull("Project id", projectId);
        Contract.RequireNotNull("Task id", taskId);
        Contract.RequireNotNull("Tag id", tagId);
        Contract.Require("Plan is not deleted", () => !_isDeleted);
        Contract.Require("Project exists", () => HasProject(projectId));

        var project = GetProject(projectId);
        Contract.Require("Task exists in project", () => project != null && project.HasTask(taskId));

        var task = project!.GetTask(taskId);
        Contract.Require("Tag is assigned", () => task != null && task.HasTag(tagId));

        Apply(new PlanEvents.TagUnassigned(
            _id,
            project.Id,
            taskId,
            tagId,
            new Dictionary<string, string>(),
            Guid.NewGuid(),
            DateProvider.Now()
        ));

        Contract.Ensure("Tag is unassigned from task", () => task != null && !task.HasTag(tagId));
    }

    public override void EnsureInvariant()
    {
        Contract.Invariant($"Category is '{CategoryValue}'.", () => Category == CategoryValue);
        Contract.InvariantNotNull("Plan Id", _id);
        if (!_isDeleted)
        {
            Contract.InvariantNotNull("Plan name", _name);
            Contract.InvariantNotNull("User Id", _userId);
        }
    }

    protected override void When(PlanEvents.IPlanEvent @event)
    {
        switch (@event)
        {
            case PlanEvents.PlanCreated e:
                _id = e.PlanId;
                _name = e.Name;
                _userId = e.UserId;
                _projects.Clear();
                _nextTaskId = 0;
                _isDeleted = false;
                break;
            case PlanEvents.PlanRenamed e:
                _name = e.NewName;
                break;
            case PlanEvents.ProjectCreated e:
                _projects[e.ProjectId] = new Project(e.ProjectId, e.ProjectName, _id);
                break;
            case PlanEvents.TaskCreated e:
                {
                    var project = GetProject(e.ProjectId) ?? GetProject(e.ProjectName);
                    if (project != null)
                    {
                        project.AddTask(new Task(e.TaskId, e.TaskName, project.Name));
                    }
                    if (int.TryParse(e.TaskId.Value, out var taskIdValue) && taskIdValue >= _nextTaskId)
                    {
                        _nextTaskId = taskIdValue + 1;
                    }
                }
                break;
            case PlanEvents.TaskChecked e:
                GetProject(e.ProjectId)?.CheckTask(e.TaskId);
                break;
            case PlanEvents.TaskUnchecked e:
                GetProject(e.ProjectId)?.UncheckTask(e.TaskId);
                break;
            case PlanEvents.TaskDeleted e:
                GetProject(e.ProjectId)?.DeleteTask(e.TaskId);
                break;
            case PlanEvents.TaskDeadlineSet e:
                {
                    var deadline = e.Deadline != null ? DateOnly.Parse(e.Deadline) : (DateOnly?)null;
                    GetProject(e.ProjectId)?.SetTaskDeadline(e.TaskId, deadline);
                }
                break;
            case PlanEvents.TaskRenamed e:
                GetProject(e.ProjectId)?.RenameTask(e.TaskId, e.NewName);
                break;
            case PlanEvents.ProjectDeleted e:
                _projects.Remove(e.ProjectId);
                break;
            case PlanEvents.PlanDeleted:
                _isDeleted = true;
                break;
            case PlanEvents.TagAssigned e:
                {
                    var task = GetProject(e.ProjectId)?.GetTask(e.TaskId);
                    task?.AssignTag(e.TagId);
                }
                break;
            case PlanEvents.TagUnassigned e:
                {
                    var task = GetProject(e.ProjectId)?.GetTask(e.TaskId);
                    task?.UnassignTag(e.TagId);
                }
                break;
            default:
                break;
        }
    }
}

// TODO: Replace these placeholders with the .NET EzDdd + uContract ports.
public abstract class EsAggregateRoot<TId, TEvent>
{
    private readonly List<TEvent> _domainEvents = new();

    protected EsAggregateRoot()
    {
    }

    protected EsAggregateRoot(IEnumerable<TEvent> domainEvents)
    {
        foreach (var @event in domainEvents)
        {
            When(@event);
        }
    }

    protected void Apply(TEvent @event)
    {
        _domainEvents.Add(@event);
        When(@event);
    }

    public IReadOnlyList<TEvent> DomainEvents => _domainEvents;
    public TEvent? LastDomainEvent => _domainEvents.Count == 0 ? default : _domainEvents[^1];

    public void ClearDomainEvents() => _domainEvents.Clear();

    public int Version { get; set; }
    public string StreamName { get; set; } = string.Empty;

    public abstract string Category { get; }
    public abstract TId Id { get; }
    public abstract bool IsDeleted { get; }

    protected abstract void When(TEvent @event);
    public abstract void EnsureInvariant();
}

public static class DateProvider
{
    public static DateTimeOffset Now() => DateTimeOffset.UtcNow;
}

public static class Contract
{
    public static void RequireNotNull(string name, object? value)
    {
        if (value is null)
        {
            throw new ArgumentNullException(name);
        }
    }

    public static void Require(string message, Func<bool> condition)
    {
        if (!condition())
        {
            throw new InvalidOperationException(message);
        }
    }

    public static void Ensure(string message, Func<bool> condition)
    {
        if (!condition())
        {
            throw new InvalidOperationException(message);
        }
    }

    public static void Invariant(string message, Func<bool> condition)
    {
        if (!condition())
        {
            throw new InvalidOperationException(message);
        }
    }

    public static void InvariantNotNull(string name, object? value)
    {
        if (value is null)
        {
            throw new InvalidOperationException($"{name} must not be null.");
        }
    }
}
