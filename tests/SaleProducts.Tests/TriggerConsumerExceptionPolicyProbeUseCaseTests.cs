using Lab.BuildingBlocks.Integrations;
using Lab.BuildingBlocks.Integrations.Diagnostics;
using Moq;
using SaleProducts.Applications.UseCases;
using Shouldly;

namespace SaleProducts.Tests;

public sealed class TriggerConsumerExceptionPolicyProbeUseCaseTests
{
    [Fact]
    public async Task given_the_probe_is_disabled_when_triggered_then_no_message_is_published()
    {
        var publisher = new Mock<IIntegrationEventPublisher>();
        var useCase = new TriggerConsumerExceptionPolicyProbeUseCase(
            new ConsumerExceptionPolicyProbeOptions(false),
            publisher.Object);

        var output = await useCase.ExecuteAsync(
            new TriggerConsumerExceptionPolicyProbeInput(
                ConsumerExceptionPolicyProbeFailureKind.Timeout),
            CancellationToken.None);

        output.Status.ShouldBe(TriggerConsumerExceptionPolicyProbeStatus.Disabled);
        output.ProbeId.ShouldBeNull();
        publisher.VerifyNoOtherCalls();
    }

    [Theory]
    [InlineData(ConsumerExceptionPolicyProbeFailureKind.Timeout)]
    [InlineData(ConsumerExceptionPolicyProbeFailureKind.Unhandled)]
    public async Task given_the_probe_is_enabled_when_triggered_then_a_correlatable_message_is_published(
        ConsumerExceptionPolicyProbeFailureKind failureKind)
    {
        var publisher = new Mock<IIntegrationEventPublisher>();
        publisher.Setup(candidate => candidate.PublishAsync(It.IsAny<IIntegrationEvent>()))
                 .Returns(Task.CompletedTask);
        var useCase = new TriggerConsumerExceptionPolicyProbeUseCase(
            new ConsumerExceptionPolicyProbeOptions(true),
            publisher.Object);

        var output = await useCase.ExecuteAsync(
            new TriggerConsumerExceptionPolicyProbeInput(failureKind),
            CancellationToken.None);

        output.Status.ShouldBe(TriggerConsumerExceptionPolicyProbeStatus.Accepted);
        output.ProbeId.ShouldNotBeNull();
        output.FailureKind.ShouldBe(failureKind);
        publisher.Verify(
            candidate => candidate.PublishAsync(
                It.Is<ConsumerExceptionPolicyProbe>(probe =>
                    probe.ProbeId == output.ProbeId && probe.FailureKind == failureKind)),
            Times.Once);
    }
}
