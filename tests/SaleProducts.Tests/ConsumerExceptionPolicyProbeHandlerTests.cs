using Lab.BuildingBlocks.Integrations.Diagnostics;
using Microsoft.Extensions.Logging.Abstractions;
using SaleOrders.Consumer.Messaging;
using Shouldly;

namespace SaleProducts.Tests;

public sealed class ConsumerExceptionPolicyProbeHandlerTests
{
    [Fact]
    public void given_a_timeout_probe_when_handled_then_a_timeout_exception_contains_the_probe_id()
    {
        var probe = CreateProbe(ConsumerExceptionPolicyProbeFailureKind.Timeout);

        var exception = Should.Throw<TimeoutException>(() =>
            ConsumerExceptionPolicyProbeHandler.Handle(
                probe,
                NullLogger<ConsumerExceptionPolicyProbeHandler>.Instance));

        exception.Message.ShouldContain(probe.ProbeId.ToString());
    }

    [Fact]
    public void given_an_unhandled_probe_when_handled_then_an_invalid_operation_exception_contains_the_probe_id()
    {
        var probe = CreateProbe(ConsumerExceptionPolicyProbeFailureKind.Unhandled);

        var exception = Should.Throw<InvalidOperationException>(() =>
            ConsumerExceptionPolicyProbeHandler.Handle(
                probe,
                NullLogger<ConsumerExceptionPolicyProbeHandler>.Instance));

        exception.Message.ShouldContain(probe.ProbeId.ToString());
    }

    private static ConsumerExceptionPolicyProbe CreateProbe(
        ConsumerExceptionPolicyProbeFailureKind failureKind)
        => new(Guid.CreateVersion7(), failureKind, DateTime.UtcNow);
}
