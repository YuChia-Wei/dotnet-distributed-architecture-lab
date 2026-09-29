using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Example.Plans.UseCases.Port;

namespace Example.Plans.UseCases;

/// <summary>查詢方案清單的 Application inbound port。</summary>
public interface IGetPlansUseCase
{
    Task<GetPlansOutput> ExecuteAsync(
        GetPlansInput input,
        CancellationToken cancellationToken);
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
