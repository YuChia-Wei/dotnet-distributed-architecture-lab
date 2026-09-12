using Microsoft.AspNetCore.Mvc;
using SaleProducts.Applications.UseCases;
using SaleProducts.WebApi.Models.Responses;

namespace SaleProducts.WebApi.Controllers;

/// <summary>發佈兩種並行 Consumer 範例使用的外部 MQ 事件。</summary>
[ApiController]
[Route("api/products/diagnostics/parallel-work")]
public sealed class ConsumerParallelDiagnosticsController(ITriggerParallelWorkProbeUseCase useCase) : ControllerBase
{
    /// <summary>發佈選定模式的外部事件；回應僅代表已接受發佈。</summary>
    [HttpPost("{mode}")]
    [ProducesResponseType<ParallelWorkProbeResponse>(StatusCodes.Status202Accepted)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<ActionResult<ParallelWorkProbeResponse>> Trigger(
        [FromRoute] ParallelWorkProbeMode mode, [FromQuery] Guid? probeId,
        CancellationToken cancellationToken)
    {
        if (!Enum.IsDefined(mode) || probeId == Guid.Empty)
            return this.BadRequest(new ProblemDetails { Status = StatusCodes.Status400BadRequest,
                Detail = "A supported mode and a non-empty probe identifier are required." });
        var output = await useCase.ExecuteAsync(new TriggerParallelWorkProbeInput(mode, probeId), cancellationToken);
        if (!output.Accepted) return this.NotFound();
        return this.Accepted(new ParallelWorkProbeResponse(output.ProbeId!.Value, mode.ToString(),
            "products.integration.events", "orders-consumer"));
    }
}
