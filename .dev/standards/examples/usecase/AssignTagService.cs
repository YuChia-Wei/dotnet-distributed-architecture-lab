using System;
using Example.Plans.Domain;
using Example.Tags.Domain;

namespace Example.Plans.UseCases;

public sealed class AssignTagService : IAssignTagUseCase
{
    private readonly IRepository<Plan, PlanId> _planRepository;
    private readonly IRepository<Tag, TagId> _tagRepository;

    public AssignTagService(IRepository<Plan, PlanId> planRepository, IRepository<Tag, TagId> tagRepository)
    {
        Contract.RequireNotNull("Plan repository", planRepository);
        Contract.RequireNotNull("Tag repository", tagRepository);
        _planRepository = planRepository;
        _tagRepository = tagRepository;
    }

    public CqrsOutput Execute(AssignTagInput input)
    {
        Contract.RequireNotNull("Input", input);
        Contract.RequireNotNull("Plan id", input.PlanId);
        Contract.RequireNotNull("Project name", input.ProjectName);
        Contract.RequireNotNull("Task id", input.TaskId);
        Contract.RequireNotNull("Tag id", input.TagId);

        var plan = _planRepository.FindById(PlanId.ValueOf(input.PlanId!))
                   ?? throw new ArgumentException($"Plan not found: {input.PlanId}");

        var tag = _tagRepository.FindById(TagId.ValueOf(input.TagId!))
                  ?? throw new ArgumentException($"Tag not found: {input.TagId}");

        var projectName = ProjectName.ValueOf(input.ProjectName!);
        var taskId = TaskId.ValueOf(input.TaskId!);

        Contract.Require("Project exists", () => plan.HasProject(projectName));
        Contract.Require("Task exists", () => plan.GetProject(projectName)?.HasTask(taskId) == true);
        Contract.Require("Tag belongs to same plan", () => tag.PlanId.Equals(plan.Id));
        Contract.Require("Tag is not deleted", () => !tag.IsDeleted);

        var project = plan.GetProject(projectName)!;
        plan.AssignTag(project.Id, taskId, TagId.ValueOf(input.TagId!));

        _planRepository.Save(plan);

        return CqrsOutput.Create()
            .SetExitCode(ExitCode.Success);
    }

    // Wolverine handler entry point
    public CqrsOutput Handle(AssignTagInput input) => Execute(input);
}

// TODO: Replace with the Tag aggregate from the ezDDD .NET port.
namespace Example.Tags.Domain
{
    public sealed class Tag
    {
        public TagId Id { get; }
        public PlanId PlanId { get; }
        public bool IsDeleted { get; private set; }

        public Tag(TagId id, PlanId planId)
        {
            Id = id;
            PlanId = planId;
        }

        public void MarkDeleted() => IsDeleted = true;
    }
}
