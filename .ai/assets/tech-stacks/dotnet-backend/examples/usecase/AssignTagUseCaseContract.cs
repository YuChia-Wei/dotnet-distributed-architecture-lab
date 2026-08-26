using System.Threading;
using System.Threading.Tasks;

namespace Example.Plans.UseCases;

/// <summary>指派標籤的 Application inbound port。</summary>
public interface IAssignTagUseCase
{
    Task<CqrsOutput> ExecuteAsync(
        AssignTagInput input,
        CancellationToken cancellationToken);
}

public sealed class AssignTagInput : IInput
{
    public string? PlanId { get; set; }
    public string? ProjectName { get; set; }
    public string? TaskId { get; set; }
    public string? TagId { get; set; }

    public static AssignTagInput Create() => new();
}
