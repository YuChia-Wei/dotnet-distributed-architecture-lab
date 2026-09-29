using System.Threading;
using System.Threading.Tasks;

namespace Example.Plans.UseCases;

/// <summary>查詢方案清單的應用流程。</summary>
public sealed class GetPlansUseCase : IGetPlansUseCase
{
    private readonly IPlanDtosProjection _planDtosProjection;

    public GetPlansUseCase(IPlanDtosProjection planDtosProjection)
    {
        _planDtosProjection = planDtosProjection;
    }

    public Task<GetPlansOutput> ExecuteAsync(
        GetPlansInput input,
        CancellationToken cancellationToken)
    {
        try
        {
            var output = GetPlansOutput.Create();
            var projectionInput = new PlanDtosProjectionInput
            {
                UserId = input.UserId,
                SortBy = input.SortBy,
                SortOrder = input.SortOrder
            };

            var plans = _planDtosProjection.Query(projectionInput);

            output.SetPlans(plans);
            output.SetExitCode(ExitCode.Success);
            return Task.FromResult(output);
        }
        catch (Exception ex)
        {
            throw new UseCaseFailureException(ex);
        }
    }
}
