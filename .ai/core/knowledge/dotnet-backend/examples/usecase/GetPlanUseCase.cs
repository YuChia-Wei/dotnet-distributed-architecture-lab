using Example.Plans.Domain;
using Example.Plans.UseCases.Port;
using System.Threading;
using System.Threading.Tasks;

namespace Example.Plans.UseCases;

/// <summary>查詢單一方案的應用流程。</summary>
public sealed class GetPlanUseCase : IGetPlanUseCase
{
    private readonly IPlanProjection _projection;

    public GetPlanUseCase(IPlanProjection projection)
    {
        Contract.RequireNotNull("Projection", projection);
        _projection = projection;
    }

    public Task<PlanDto?> ExecuteAsync(
        GetPlanInput input,
        CancellationToken cancellationToken)
    {
        Contract.RequireNotNull("Input", input);
        Contract.RequireNotNull("Plan id", input.PlanId);
        Contract.Require("Plan id is not empty", () => !string.IsNullOrWhiteSpace(input.PlanId));

        var plan = _projection.FindById(input.PlanId!);

        Contract.Ensure("Plan found or null", () => plan == null || plan.Id == input.PlanId);
        return Task.FromResult(plan);
    }
}
