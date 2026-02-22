using Example.Plans.UseCases.Port;

namespace Example.Plans.UseCases;

public interface IGetPlanUseCase : IQuery<GetPlanInput, PlanDto?>
{
    PlanDto? Execute(GetPlanInput input);
}

public sealed class GetPlanInput : IInput
{
    public string? PlanId { get; set; }

    public static GetPlanInput Create() => new();
}
