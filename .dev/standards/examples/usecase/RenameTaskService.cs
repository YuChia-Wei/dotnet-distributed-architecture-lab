using Example.Plans.Domain;

namespace Example.Plans.UseCases;

public sealed class RenameTaskService : IRenameTaskUseCase
{
    private readonly IRepository<Plan, PlanId> _repository;

    public RenameTaskService(IRepository<Plan, PlanId> repository)
    {
        Contract.RequireNotNull("Repository", repository);
        _repository = repository;
    }

    public CqrsOutput Execute(RenameTaskInput input)
    {
        Contract.RequireNotNull("Input", input);
        Contract.RequireNotNull("Plan id", input.PlanId);
        Contract.RequireNotNull("Project name", input.ProjectName);
        Contract.RequireNotNull("Task id", input.TaskId);
        Contract.RequireNotNull("New task name", input.NewTaskName);
        Contract.Require("New task name is not empty", () => !string.IsNullOrWhiteSpace(input.NewTaskName));

        var plan = _repository.FindById(PlanId.ValueOf(input.PlanId!))
                   ?? throw new ArgumentException($"Plan not found: {input.PlanId}");

        var projectName = ProjectName.ValueOf(input.ProjectName!);
        var taskId = TaskId.ValueOf(input.TaskId!);

        Contract.Require("Project exists", () => plan.HasProject(projectName));
        Contract.Require("Task exists", () => plan.GetProject(projectName)?.HasTask(taskId) == true);

        plan.RenameTask(projectName, taskId, input.NewTaskName!);
        _repository.Save(plan);

        return CqrsOutput.Create()
            .SetExitCode(ExitCode.Success);
    }

    // Wolverine handler entry point
    public CqrsOutput Handle(RenameTaskInput input) => Execute(input);
}
