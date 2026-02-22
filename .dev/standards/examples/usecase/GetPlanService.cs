using Example.Plans.Domain;
using Example.Plans.UseCases.Port;

namespace Example.Plans.UseCases;

public sealed class GetPlanService : IGetPlanUseCase
{
    private readonly IPlanProjection _projection;

    public GetPlanService(IPlanProjection projection)
    {
        Contract.RequireNotNull("Projection", projection);
        _projection = projection;
    }

    public PlanDto? Execute(GetPlanInput input)
    {
        Contract.RequireNotNull("Input", input);
        Contract.RequireNotNull("Plan id", input.PlanId);
        Contract.Require("Plan id is not empty", () => !string.IsNullOrWhiteSpace(input.PlanId));

        var plan = _projection.FindById(input.PlanId!);

        Contract.Ensure("Plan found or null", () => plan == null || plan.Id == input.PlanId);
        return plan;
    }

    // Wolverine handler entry point
    public PlanDto? Handle(GetPlanInput input) => Execute(input);
}
