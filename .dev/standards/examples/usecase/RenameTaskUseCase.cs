namespace Example.Plans.UseCases;

public interface IRenameTaskUseCase : ICommand<RenameTaskInput, CqrsOutput>
{
    CqrsOutput Execute(RenameTaskInput input);
}

public sealed class RenameTaskInput : IInput
{
    public string? PlanId { get; set; }
    public string? ProjectName { get; set; }
    public string? TaskId { get; set; }
    public string? NewTaskName { get; set; }

    public static RenameTaskInput Create() => new();
}
