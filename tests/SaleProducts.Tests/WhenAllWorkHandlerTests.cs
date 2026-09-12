using Lab.BuildingBlocks.Integrations.Diagnostics;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.DependencyInjection.Extensions;
using SaleOrders.Applications.Diagnostics;
using SaleOrders.Consumer.Diagnostics;
using Shouldly;

namespace SaleProducts.Tests;

public sealed class WhenAllWorkHandlerTests
{
    [Fact]
    public async Task Given_two_gated_work_items_When_handling_Then_both_start_in_distinct_scopes_and_completion_waits_for_both()
    {
        var state = new ParallelWorkProbeState();
        var probe = state.GivenProbe();
        await using var services = GivenServices(state);
        var handling = WhenHandling(probe, services, TestContext.Current.CancellationToken);
        try
        {
            await probe.WhenBothStartedAsync();
            probe.AuditScopes.Single().ShouldNotBe(probe.StatisticsScopes.Single());
            handling.IsCompleted.ShouldBeFalse();
            probe.AuditRelease.SetResult();
            await probe.AuditCompleted.Task.WaitAsync(TimeSpan.FromSeconds(5), TestContext.Current.CancellationToken);
            handling.IsCompleted.ShouldBeFalse();
            probe.StatisticsRelease.SetResult();
            await handling.WaitAsync(TimeSpan.FromSeconds(5), TestContext.Current.CancellationToken);
            probe.DisposedScopes.Count.ShouldBe(2);
            state.Store.AuditCount.ShouldBe(1);
            state.Store.StatisticsCount.ShouldBe(1);
        }
        finally { probe.ReleaseBoth(); }
    }

    [Fact]
    public async Task Given_a_synchronous_branch_failure_When_handling_Then_the_other_branch_is_awaited_and_scopes_are_disposed()
    {
        var state = new ParallelWorkProbeState();
        var probe = new ParallelProbe { ThrowStatisticsSynchronously = true };
        state.Probes[probe.Id] = probe;
        await using var services = GivenServices(state);
        var handling = WhenHandling(probe, services, TestContext.Current.CancellationToken);
        try
        {
            await probe.WhenBothStartedAsync();
            handling.IsCompleted.ShouldBeFalse();
            probe.AuditRelease.SetResult();
            await Should.ThrowAsync<InvalidOperationException>(() => handling);
            probe.DisposedScopes.Count.ShouldBe(2);
            state.Store.AuditCount.ShouldBe(1);
            state.Store.StatisticsCount.ShouldBe(0);
        }
        finally { probe.ReleaseBoth(); }
    }

    [Fact]
    public async Task Given_inflight_branches_When_cancelled_Then_both_stop_and_all_scopes_are_disposed()
    {
        var state = new ParallelWorkProbeState();
        var probe = state.GivenProbe();
        await using var services = GivenServices(state);
        using var cancellation = CancellationTokenSource.CreateLinkedTokenSource(TestContext.Current.CancellationToken);
        var handling = WhenHandling(probe, services, cancellation.Token);
        await probe.WhenBothStartedAsync();
        await cancellation.CancelAsync();
        await Should.ThrowAsync<OperationCanceledException>(() => handling);
        probe.DisposedScopes.Count.ShouldBe(2);
        state.Store.AuditCount.ShouldBe(0);
        state.Store.StatisticsCount.ShouldBe(0);
    }

    [Fact]
    public async Task Given_a_partially_successful_delivery_When_retried_Then_both_run_again_but_effects_are_idempotent()
    {
        var state = new ParallelWorkProbeState();
        var probe = state.GivenProbe(failStatisticsOnce: true);
        probe.ReleaseBoth();
        await using var services = GivenServices(state);
        await Should.ThrowAsync<TimeoutException>(() => WhenHandling(probe, services, TestContext.Current.CancellationToken));
        await WhenHandling(probe, services, TestContext.Current.CancellationToken);
        probe.AuditAttempts.ShouldBe(2);
        probe.StatisticsAttempts.ShouldBe(2);
        state.Store.AuditCount.ShouldBe(1);
        state.Store.StatisticsCount.ShouldBe(1);
        probe.DisposedScopes.Count.ShouldBe(4);
    }

    private static ServiceProvider GivenServices(ParallelWorkProbeState state)
    {
        var services = new ServiceCollection();
        services.AddLogging();
        services.AddParallelWorkExamples();
        services.AddSingleton(state);
        services.RemoveAll<IParallelAuditWriter>();
        services.RemoveAll<IParallelStatisticsWriter>();
        services.AddScoped<IParallelAuditWriter, GatedAuditWriter>();
        services.AddScoped<IParallelStatisticsWriter, GatedStatisticsWriter>();
        return services.BuildServiceProvider(new ServiceProviderOptions { ValidateScopes = true, ValidateOnBuild = true });
    }

    private static Task WhenHandling(ParallelProbe probe, IServiceProvider services, CancellationToken cancellationToken)
        => WhenAllWorkHandler.Handle(new WhenAllWorkRequested(probe.Id, DateTime.UtcNow),
            services.GetRequiredService<IServiceScopeFactory>(), cancellationToken);
}
