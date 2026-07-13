using System.Threading;
using System.Threading.Tasks;

namespace Example.Plans.UseCases;

/// <summary>重新命名任務的 Application inbound port。</summary>
public interface IRenameTaskUseCase
{
    Task<CqrsOutput> ExecuteAsync(
        RenameTaskInput input,
        CancellationToken cancellationToken);
}

public sealed class RenameTaskInput : IInput
{
    public string? PlanId { get; set; }
    public string? ProjectName { get; set; }
    public string? TaskId { get; set; }
    public string? NewTaskName { get; set; }

    public static RenameTaskInput Create() => new();
}
