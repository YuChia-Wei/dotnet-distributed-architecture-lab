using System.Collections.Generic;

namespace Example.Plans.UseCases.Port;

// Basic DTO template: pure data container, no domain logic.
public sealed class PlanDto
{
    private readonly List<ProjectDto> _projects = new();

    public string Id { get; private set; } = string.Empty;
    public string Name { get; private set; } = string.Empty;
    public string UserId { get; private set; } = string.Empty;
    public IReadOnlyList<ProjectDto> Projects => _projects;

    public PlanDto SetId(string id)
    {
        Id = id;
        return this;
    }

    public PlanDto SetName(string name)
    {
        Name = name;
        return this;
    }

    public PlanDto SetUserId(string userId)
    {
        UserId = userId;
        return this;
    }

    public PlanDto SetProjects(IEnumerable<ProjectDto> projects)
    {
        _projects.Clear();
        _projects.AddRange(projects);
        return this;
    }

    public PlanDto AddProject(ProjectDto project)
    {
        _projects.Add(project);
        return this;
    }

    public PlanDto ClearProjects()
    {
        _projects.Clear();
        return this;
    }
}
