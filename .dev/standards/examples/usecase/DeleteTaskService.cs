using Example.Plans.Domain;

namespace Example.Plans.UseCases;

public sealed class DeleteTaskService : IDeleteTaskUseCase
{
    private readonly IRepository<Plan, PlanId> _repository;

    public DeleteTaskService(IRepository<Plan, PlanId> repository)
    {
        Contract.RequireNotNull("Repository", repository);
        _repository = repository;
    }

    public CqrsOutput Execute(DeleteTaskInput input)
    {
        Contract.RequireNotNull("Input", input);
        Contract.RequireNotNull("Plan id", input.PlanId);
        Contract.RequireNotNull("Project name", input.ProjectName);
        Contract.RequireNotNull("Task id", input.TaskId);

        var plan = _repository.FindById(PlanId.ValueOf(input.PlanId!))
                   ?? throw new ArgumentException($"Plan not found: {input.PlanId}");

        var projectName = ProjectName.ValueOf(input.ProjectName!);
        var taskId = TaskId.ValueOf(input.TaskId!);

        Contract.Require("Project exists", () => plan.HasProject(projectName));
        Contract.Require("Task exists", () => plan.GetProject(projectName)?.HasTask(taskId) == true);

        plan.DeleteTask(projectName, taskId);
        _repository.Save(plan);

        return CqrsOutput.Create()
            .SetExitCode(ExitCode.Success);
    }

    // Wolverine handler entry point
    public CqrsOutput Handle(DeleteTaskInput input) => Execute(input);
}
