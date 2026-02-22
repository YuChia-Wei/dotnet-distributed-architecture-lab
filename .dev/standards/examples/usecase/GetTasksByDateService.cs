using System.Linq;
using Example.Plans.Domain;

namespace Example.Plans.UseCases;

public sealed class GetTasksByDateService : IGetTasksByDateUseCase
{
    private readonly ITasksByDateProjection _projection;

    public GetTasksByDateService(ITasksByDateProjection projection)
    {
        Contract.RequireNotNull("Projection", projection);
        _projection = projection;
    }

    public GetTasksByDateOutput Execute(GetTasksByDateInput input)
    {
        Contract.RequireNotNull("Input", input);
        Contract.RequireNotNull("User id", input.UserId);
        Contract.RequireNotNull("Target date", input.TargetDate);
        Contract.Require("User id is not empty", () => !string.IsNullOrWhiteSpace(input.UserId));

        var tasks = _projection.FindTasksByDate(input.UserId!, input.TargetDate!.Value);

        var output = GetTasksByDateOutput.Create();
        output.SetTasks(tasks);
        output.SetExitCode(ExitCode.Success);

        Contract.Ensure("Tasks list is not null", () => output.Tasks != null);
        Contract.Ensure("All tasks match the target date", () =>
            output.Tasks.All(task => task.Deadline.HasValue && task.Deadline == input.TargetDate));

        return output;
    }

    // Wolverine handler entry point
    public GetTasksByDateOutput Handle(GetTasksByDateInput input) => Execute(input);
}
