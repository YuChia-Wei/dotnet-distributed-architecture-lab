using System.Threading;
using System.Threading.Tasks;

namespace Example.Plans.UseCases;

/// <summary>建立方案的 Application inbound port。</summary>
public interface ICreatePlanUseCase
{
    Task<CqrsOutput> ExecuteAsync(
        CreatePlanInput input,
        CancellationToken cancellationToken);
}

public sealed class CreatePlanInput : IInput
{
    public string? Id { get; set; }
    public string? Name { get; set; }
    public string? UserId { get; set; }

    public static CreatePlanInput Create() => new();
}
