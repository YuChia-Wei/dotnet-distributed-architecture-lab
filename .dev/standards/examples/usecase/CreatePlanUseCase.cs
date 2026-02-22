namespace Example.Plans.UseCases;

public interface ICreatePlanUseCase : ICommand<CreatePlanInput, CqrsOutput>
{
    CqrsOutput Execute(CreatePlanInput input);
}

public sealed class CreatePlanInput : IInput
{
    public string? Id { get; set; }
    public string? Name { get; set; }
    public string? UserId { get; set; }

    public static CreatePlanInput Create() => new();
}
