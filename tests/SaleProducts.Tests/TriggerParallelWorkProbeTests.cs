using Lab.BuildingBlocks.Integrations;
using Lab.BuildingBlocks.Integrations.Diagnostics;
using Moq;
using SaleProducts.Applications.UseCases;
using Shouldly;

namespace SaleProducts.Tests;

public sealed class TriggerParallelWorkProbeTests
{
    [Theory]
    [InlineData(ParallelWorkProbeMode.WhenAll)]
    [InlineData(ParallelWorkProbeMode.IndependentHandlers)]
    public async Task Given_enabled_publication_When_requested_Then_the_selected_external_event_preserves_the_replay_identifier(ParallelWorkProbeMode mode)
    {
        var publisher = new Mock<IIntegrationEventPublisher>();
        var useCase = new TriggerParallelWorkProbeUseCase(new ParallelWorkProbeOptions(true), publisher.Object);
        var id = Guid.NewGuid();
        var output = await useCase.ExecuteAsync(new TriggerParallelWorkProbeInput(mode, id), TestContext.Current.CancellationToken);
        output.Accepted.ShouldBeTrue();
        output.ProbeId.ShouldBe(id);
        if (mode == ParallelWorkProbeMode.WhenAll)
            publisher.Verify(x => x.PublishAsync(It.Is<WhenAllWorkRequested>(e => e.ProbeId == id)), Times.Once);
        else
            publisher.Verify(x => x.PublishAsync(It.Is<IndependentWorkRequested>(e => e.ProbeId == id)), Times.Once);
        publisher.VerifyNoOtherCalls();
    }

    [Fact]
    public async Task Given_disabled_publication_When_requested_Then_no_event_is_published()
    {
        var publisher = new Mock<IIntegrationEventPublisher>();
        var useCase = new TriggerParallelWorkProbeUseCase(new ParallelWorkProbeOptions(false), publisher.Object);
        var output = await useCase.ExecuteAsync(new TriggerParallelWorkProbeInput(ParallelWorkProbeMode.WhenAll, null), TestContext.Current.CancellationToken);
        output.Accepted.ShouldBeFalse();
        output.ProbeId.ShouldBeNull();
        publisher.VerifyNoOtherCalls();
    }

    [Fact]
    public async Task Given_cancelled_request_When_triggered_Then_no_event_is_published()
    {
        var publisher = new Mock<IIntegrationEventPublisher>();
        var useCase = new TriggerParallelWorkProbeUseCase(new ParallelWorkProbeOptions(true), publisher.Object);
        using var cancelled = new CancellationTokenSource();
        await cancelled.CancelAsync();
        await Should.ThrowAsync<OperationCanceledException>(() => useCase.ExecuteAsync(
            new TriggerParallelWorkProbeInput(ParallelWorkProbeMode.IndependentHandlers, null), cancelled.Token));
        publisher.VerifyNoOtherCalls();
    }
}
