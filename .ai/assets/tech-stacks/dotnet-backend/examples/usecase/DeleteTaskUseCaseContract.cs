using System.Threading;
using System.Threading.Tasks;

namespace Example.Plans.UseCases;

/// <summary>刪除任務的 Application inbound port。</summary>
public interface IDeleteTaskUseCase
{
    Task<CqrsOutput> ExecuteAsync(
        DeleteTaskInput input,
        CancellationToken cancellationToken);
}

public sealed class DeleteTaskInput : IInput
{
    public string? PlanId { get; set; }
    public string? ProjectName { get; set; }
    public string? TaskId { get; set; }
}
