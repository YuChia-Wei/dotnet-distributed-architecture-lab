namespace Example.Plans.UseCases;

public interface IAssignTagUseCase : ICommand<AssignTagInput, CqrsOutput>
{
    CqrsOutput Execute(AssignTagInput input);
}

public sealed class AssignTagInput : IInput
{
    public string? PlanId { get; set; }
    public string? ProjectName { get; set; }
    public string? TaskId { get; set; }
    public string? TagId { get; set; }

    public static AssignTagInput Create() => new();
}
