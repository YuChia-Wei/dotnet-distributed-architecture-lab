using System.Collections.Generic;
using Example.Plans.UseCases.Port;

namespace Example.Plans.UseCases;

public interface IGetTasksByDateUseCase : IQuery<GetTasksByDateInput, GetTasksByDateOutput>
{
    GetTasksByDateOutput Execute(GetTasksByDateInput input);
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
