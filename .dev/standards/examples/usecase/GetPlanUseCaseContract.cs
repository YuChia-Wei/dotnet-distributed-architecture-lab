using Example.Plans.UseCases.Port;
using System.Threading;
using System.Threading.Tasks;

namespace Example.Plans.UseCases;

/// <summary>查詢單一方案的 Application inbound port。</summary>
public interface IGetPlanUseCase
{
    Task<PlanDto?> ExecuteAsync(
        GetPlanInput input,
        CancellationToken cancellationToken);
}

public sealed class GetPlanInput : IInput
{
    public string? PlanId { get; set; }

    public static GetPlanInput Create() => new();
}
