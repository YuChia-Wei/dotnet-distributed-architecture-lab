using System;
using System.Threading;
using System.Threading.Tasks;
using Example.Plans.Domain;
using Example.Tags.Domain;

namespace Example.Plans.UseCases;

/// <summary>指派標籤的應用流程。</summary>
public sealed class AssignTagUseCase : IAssignTagUseCase
{
    private readonly IAggregateRepository<Plan, PlanId> _planRepository;
    private readonly IAggregateRepository<Tag, TagId> _tagRepository;

    public AssignTagUseCase(
        IAggregateRepository<Plan, PlanId> planRepository,
        IAggregateRepository<Tag, TagId> tagRepository)
    {
        Contract.RequireNotNull("Plan repository", planRepository);
        Contract.RequireNotNull("Tag repository", tagRepository);
        _planRepository = planRepository;
        _tagRepository = tagRepository;
    }

    public async Task<CqrsOutput> ExecuteAsync(
        AssignTagInput input,
        CancellationToken cancellationToken)
    {
        Contract.RequireNotNull("Input", input);
        Contract.RequireNotNull("Plan id", input.PlanId);
        Contract.RequireNotNull("Project name", input.ProjectName);
        Contract.RequireNotNull("Task id", input.TaskId);
        Contract.RequireNotNull("Tag id", input.TagId);

        var plan = await _planRepository.FindByIdAsync(
                       PlanId.ValueOf(input.PlanId!),
                       cancellationToken)
                   ?? throw new ArgumentException($"Plan not found: {input.PlanId}");

        var tag = await _tagRepository.FindByIdAsync(
                      TagId.ValueOf(input.TagId!),
                      cancellationToken)
                  ?? throw new ArgumentException($"Tag not found: {input.TagId}");

        var projectName = ProjectName.ValueOf(input.ProjectName!);
        var taskId = TaskId.ValueOf(input.TaskId!);

        Contract.Require("Project exists", () => plan.HasProject(projectName));
        Contract.Require("Task exists", () => plan.GetProject(projectName)?.HasTask(taskId) == true);
        Contract.Require("Tag belongs to same plan", () => tag.PlanId.Equals(plan.Id));
        Contract.Require("Tag is not deleted", () => !tag.IsDeleted);

        var project = plan.GetProject(projectName)!;
        plan.AssignTag(project.Id, taskId, TagId.ValueOf(input.TagId!));

        await _planRepository.SaveAsync(plan, cancellationToken);

        return CqrsOutput.Create()
            .SetExitCode(ExitCode.Success);
    }
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
