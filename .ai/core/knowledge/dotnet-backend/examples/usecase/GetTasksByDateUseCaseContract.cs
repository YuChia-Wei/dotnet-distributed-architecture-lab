using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Example.Plans.UseCases.Port;

namespace Example.Plans.UseCases;

/// <summary>依日期查詢任務的 Application inbound port。</summary>
public interface IGetTasksByDateUseCase
{
    Task<GetTasksByDateOutput> ExecuteAsync(
        GetTasksByDateInput input,
        CancellationToken cancellationToken);
}

public sealed class GetTasksByDateInput : IInput
{
    public string? UserId { get; set; }
    public DateOnly? TargetDate { get; set; }

    public static GetTasksByDateInput Create() => new();
}

public sealed class GetTasksByDateOutput : CqrsOutput
{
    public IReadOnlyList<TaskDto> Tasks { get; private set; } = new List<TaskDto>();

    public static GetTasksByDateOutput Create() => new();

    public GetTasksByDateOutput SetTasks(IEnumerable<TaskDto> tasks)
    {
        Tasks = new List<TaskDto>(tasks);
        return this;
    }
}
