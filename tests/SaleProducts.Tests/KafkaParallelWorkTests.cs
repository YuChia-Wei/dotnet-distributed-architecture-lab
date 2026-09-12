using Lab.BuildingBlocks.Integrations.Diagnostics;
using Shouldly;

namespace SaleProducts.Tests;

public sealed class KafkaParallelWorkTests(KafkaParallelFixture fixture) : IClassFixture<KafkaParallelFixture>
{
    [KafkaParallelFact]
    public async Task Given_one_external_event_When_Kafka_delivers_Then_two_original_event_handlers_overlap_in_independent_scopes()
    {
        var probe = fixture.State.GivenProbe();
        try
        {
            await fixture.PublishAsync(new IndependentWorkRequested(probe.Id, DateTime.UtcNow));
            await probe.WhenBothStartedAsync();
            probe.AuditCompleted.Task.IsCompleted.ShouldBeFalse();
            probe.StatisticsCompleted.Task.IsCompleted.ShouldBeFalse();
            probe.AuditScopes.Single().ShouldNotBe(probe.StatisticsScopes.Single());
            probe.ReleaseBoth();
            await probe.WhenBothCompletedAsync();
            probe.AuditAttempts.ShouldBe(1);
            probe.StatisticsAttempts.ShouldBe(1);
        }
        finally { probe.ReleaseBoth(); }
    }

    [KafkaParallelFact]
    public async Task Given_statistics_fails_once_When_external_event_handlers_retry_Then_successful_audit_does_not_run_again()
    {
        var probe = fixture.State.GivenProbe(failStatisticsOnce: true);
        try
        {
            await fixture.PublishAsync(new IndependentWorkRequested(probe.Id, DateTime.UtcNow));
            await probe.WhenBothStartedAsync();
            probe.AuditRelease.SetResult();
            await probe.AuditCompleted.Task.WaitAsync(TimeSpan.FromSeconds(10), TestContext.Current.CancellationToken);
            probe.StatisticsRelease.SetResult();
            await probe.WhenBothCompletedAsync();
            probe.AuditAttempts.ShouldBe(1);
            probe.StatisticsAttempts.ShouldBe(2);
            probe.StatisticsScopes.ShouldNotContain(probe.AuditScopes.Single());
        }
        finally { probe.ReleaseBoth(); }
    }

    [KafkaParallelFact]
    public async Task Given_WhenAll_event_from_Kafka_When_statistics_fails_Then_whole_delivery_retries_both_branches()
    {
        var probe = fixture.State.GivenProbe(failStatisticsOnce: true);
        try
        {
            await fixture.PublishAsync(new WhenAllWorkRequested(probe.Id, DateTime.UtcNow));
            await probe.WhenBothStartedAsync();
            probe.ReleaseBoth();
            await probe.WhenBothCompletedAsync();
            await ThenEventuallyAsync(() => probe.AuditAttempts == 2 && probe.StatisticsAttempts == 2);
            probe.AuditScopes.Intersect(probe.StatisticsScopes).ShouldBeEmpty();
        }
        finally { probe.ReleaseBoth(); }
    }

    [KafkaParallelFact]
    public async Task Given_duplicate_external_events_When_both_handlers_receive_each_delivery_Then_each_effect_is_applied_once()
    {
        var probe = fixture.State.GivenProbe();
        probe.ReleaseBoth();
        var auditBefore = fixture.State.Store.AuditCount;
        var statisticsBefore = fixture.State.Store.StatisticsCount;
        var message = new IndependentWorkRequested(probe.Id, DateTime.UtcNow);
        await fixture.PublishAsync(message);
        await probe.WhenBothCompletedAsync();
        await fixture.PublishAsync(message);
        await ThenEventuallyAsync(() => probe.AuditAttempts == 2 && probe.StatisticsAttempts == 2
            && probe.DisposedScopes.Count >= 4);
        fixture.State.Store.AuditCount.ShouldBe(auditBefore + 1);
        fixture.State.Store.StatisticsCount.ShouldBe(statisticsBefore + 1);
    }

    private static async Task ThenEventuallyAsync(Func<bool> assertion)
    {
        using var timeout = CancellationTokenSource.CreateLinkedTokenSource(TestContext.Current.CancellationToken);
        timeout.CancelAfter(TimeSpan.FromSeconds(15));
        while (!assertion()) await Task.Delay(20, timeout.Token);
    }
}
