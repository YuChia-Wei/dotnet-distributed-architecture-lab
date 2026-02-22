using System.Collections.Generic;
using Example.Plans.UseCases.Port;

namespace Example.Plans.UseCases;

public interface IGetPlansUseCase : IQuery<GetPlansInput, GetPlansOutput>
{
    GetPlansOutput Execute(GetPlansInput input);
}

public sealed class GetPlansInput : IInput
{
    public string? UserId { get; set; }
    public string? SortBy { get; set; }
    public string? SortOrder { get; set; }

    public static GetPlansInput Create() => new();
}

public sealed class GetPlansOutput : CqrsOutput
{
    public IReadOnlyList<PlanDto> Plans { get; private set; } = new List<PlanDto>();

    public static GetPlansOutput Create() => new();

    public GetPlansOutput SetPlans(IEnumerable<PlanDto> plans)
    {
        Plans = new List<PlanDto>(plans);
        return this;
    }
}
