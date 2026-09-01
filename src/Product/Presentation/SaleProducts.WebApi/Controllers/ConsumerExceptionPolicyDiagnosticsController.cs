using Lab.BuildingBlocks.Integrations.Diagnostics;
using Microsoft.AspNetCore.Mvc;
using SaleProducts.Applications.UseCases;
using SaleProducts.WebApi.Models.Responses;

namespace SaleProducts.WebApi.Controllers;

/// <summary>Exposes lab-only probes for learning Wolverine consumer failure policies.</summary>
[ApiController]
[Route("api/products/diagnostics/consumer-exception-policy")]
public sealed class ConsumerExceptionPolicyDiagnosticsController : ControllerBase
{
    /// <summary>Publishes a probe that deliberately fails in the Orders consumer.</summary>
    /// <param name="failureKind">The policy branch to exercise.</param>
    /// <param name="useCase">The probe trigger use case.</param>
    /// <param name="cancellationToken">The request cancellation token.</param>
    [HttpPost("{failureKind}")]
    [ProducesResponseType<ConsumerExceptionPolicyProbeResponse>(StatusCodes.Status202Accepted)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<ActionResult<ConsumerExceptionPolicyProbeResponse>> Trigger(
        [FromRoute] ConsumerExceptionPolicyProbeFailureKind failureKind,
        [FromServices] ITriggerConsumerExceptionPolicyProbeUseCase useCase,
        CancellationToken cancellationToken)
    {
        var output = await useCase.ExecuteAsync(
            new TriggerConsumerExceptionPolicyProbeInput(failureKind),
            cancellationToken);

        if (output.Status == TriggerConsumerExceptionPolicyProbeStatus.Disabled)
        {
            return this.NotFound();
        }

        var response = new ConsumerExceptionPolicyProbeResponse(
            output.ProbeId!.Value,
            output.FailureKind.ToString(),
            "products.integration.events",
            "orders-consumer");

        return this.Accepted(response);
    }
}
