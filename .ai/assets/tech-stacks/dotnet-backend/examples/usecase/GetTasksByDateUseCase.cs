using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Example.Plans.Domain;

namespace Example.Plans.UseCases;

/// <summary>依日期查詢任務的應用流程。</summary>
public sealed class GetTasksByDateUseCase : IGetTasksByDateUseCase
{
    private readonly ITasksByDateProjection _projection;

    public GetTasksByDateUseCase(ITasksByDateProjection projection)
    {
        Contract.RequireNotNull("Projection", projection);
        _projection = projection;
    }

    public Task<GetTasksByDateOutput> ExecuteAsync(
        GetTasksByDateInput input,
        CancellationToken cancellationToken)
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

        return Task.FromResult(output);
    }
}
