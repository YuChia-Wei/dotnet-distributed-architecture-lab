using Example.Plans.Domain;
using System.Threading;
using System.Threading.Tasks;

namespace Example.Plans.UseCases;

/// <summary>建立任務的 Application inbound port。</summary>
public interface ICreateTaskUseCase
{
    Task<CqrsOutput> ExecuteAsync(
        CreateTaskInput input,
        CancellationToken cancellationToken);
}

public sealed class CreateTaskInput : IInput
{
    public PlanId? PlanId { get; set; }
    public ProjectName? ProjectName { get; set; }
    public string? TaskName { get; set; }

    public static CreateTaskInput Create() => new();
}
