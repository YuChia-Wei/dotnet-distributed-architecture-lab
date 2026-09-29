using Example.Plans.Domain;
using System.Threading;
using System.Threading.Tasks;

namespace Example.Plans.UseCases;

/// <summary>重新命名任務的應用流程。</summary>
public sealed class RenameTaskUseCase : IRenameTaskUseCase
{
    private readonly IAggregateRepository<Plan, PlanId> _repository;

    public RenameTaskUseCase(IAggregateRepository<Plan, PlanId> repository)
    {
        Contract.RequireNotNull("Repository", repository);
        _repository = repository;
    }

    public async Task<CqrsOutput> ExecuteAsync(
        RenameTaskInput input,
        CancellationToken cancellationToken)
    {
        Contract.RequireNotNull("Input", input);
        Contract.RequireNotNull("Plan id", input.PlanId);
        Contract.RequireNotNull("Project name", input.ProjectName);
        Contract.RequireNotNull("Task id", input.TaskId);
        Contract.RequireNotNull("New task name", input.NewTaskName);
        Contract.Require("New task name is not empty", () => !string.IsNullOrWhiteSpace(input.NewTaskName));

        var plan = await _repository.FindByIdAsync(
                       PlanId.ValueOf(input.PlanId!),
                       cancellationToken)
                   ?? throw new ArgumentException($"Plan not found: {input.PlanId}");

        var projectName = ProjectName.ValueOf(input.ProjectName!);
        var taskId = TaskId.ValueOf(input.TaskId!);

        Contract.Require("Project exists", () => plan.HasProject(projectName));
        Contract.Require("Task exists", () => plan.GetProject(projectName)?.HasTask(taskId) == true);

        plan.RenameTask(projectName, taskId, input.NewTaskName!);
        await _repository.SaveAsync(plan, cancellationToken);

        return CqrsOutput.Create()
            .SetExitCode(ExitCode.Success);
    }
}
