namespace Example.Plans.UseCases;

public sealed class GetPlansService : IGetPlansUseCase
{
    private readonly IPlanDtosProjection _planDtosProjection;

    public GetPlansService(IPlanDtosProjection planDtosProjection)
    {
        _planDtosProjection = planDtosProjection;
    }

    public GetPlansOutput Execute(GetPlansInput input)
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
            return output;
        }
        catch (Exception ex)
        {
            throw new UseCaseFailureException(ex);
        }
    }

    // Wolverine handler entry point
    public GetPlansOutput Handle(GetPlansInput input) => Execute(input);
}
