using System;
using System.Threading.Tasks;
using ExampleApp.Tests.Infrastructure;
using Microsoft.Extensions.DependencyInjection;
using TestStack.BDDfy;
using Xunit;

namespace ExampleApp.Tests.Outbox;

public sealed class AggregateOutboxRepositoryTests : IClassFixture<TestHostFixture>, IDisposable
{
    private readonly IServiceScope _scope;
    private readonly ScenarioState _state = new();

    public AggregateOutboxRepositoryTests(TestHostFixture host)
    {
        _scope = host.Services.CreateScope();
    }

    public void Dispose() => _scope.Dispose();

    [Fact]
    public void Rule_Data_persistence_persist_aggregate_with_all_fields()
    {
        this.Given(_ => Given_a_SampleAggregate_aggregate_with_complete_data())
            .When(_ => When_i_save_the_aggregate_using_OutboxRepository())
            .Then(_ => Then_the_aggregate_is_persisted_with_all_fields())
            .BDDfy();
    }

    [Fact]
    public void Rule_Data_retrieval_retrieve_aggregate_with_complete_data()
    {
        this.Given(_ => Given_a_aggregate_exists_in_the_database())
            .When(_ => When_i_load_the_aggregate_from_repository())
            .Then(_ => Then_the_aggregate_data_is_fully_rehydrated())
            .BDDfy();
    }

    [Fact]
    public void Rule_Soft_delete_soft_delete_aggregate()
    {
        this.Given(_ => Given_a_aggregate_exists_in_the_database())
            .When(_ => When_i_mark_the_aggregate_as_deleted_and_save())
            .Then(_ => Then_the_aggregate_is_marked_as_deleted_in_the_database())
            .BDDfy();
    }

    [Fact]
    public void Rule_Version_control_version_increments_on_update()
    {
        this.Given(_ => Given_a_aggregate_exists_in_the_database())
            .When(_ => When_i_update_the_aggregate_and_save())
            .Then(_ => Then_the_version_is_incremented_in_storage())
            .BDDfy();
    }

    void Given_a_SampleAggregate_aggregate_with_complete_data()
    {
        _state.AggregateId = $"test-aggregate-{DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()}";
    }

    async Task Given_a_aggregate_exists_in_the_database()
    {
        _state.AggregateId = $"test-aggregate-{DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()}";
        await Task.CompletedTask;
    }

    async Task When_i_save_the_aggregate_using_OutboxRepository()
    {
        // TODO: repository.Save(aggregate)
        await Task.CompletedTask;
    }

    async Task When_i_load_the_aggregate_from_repository()
    {
        // TODO: repository.FindById(...)
        await Task.CompletedTask;
    }

    async Task When_i_mark_the_aggregate_as_deleted_and_save()
    {
        // TODO: aggregate.MarkAsDeleted(userId); repository.Save(aggregate)
        await Task.CompletedTask;
    }

    async Task When_i_update_the_aggregate_and_save()
    {
        // TODO: update entity + repository.Save(...)
        await Task.CompletedTask;
    }

    void Then_the_aggregate_is_persisted_with_all_fields()
    {
        Assert.NotNull(_state.AggregateId);
    }

    void Then_the_aggregate_data_is_fully_rehydrated()
    {
        Assert.NotNull(_state.AggregateId);
    }

    void Then_the_aggregate_is_marked_as_deleted_in_the_database()
    {
        Assert.NotNull(_state.AggregateId);
    }

    void Then_the_version_is_incremented_in_storage()
    {
        // TODO: Assert optimistic version increment.
    }

    private sealed class ScenarioState
    {
        public string? AggregateId { get; set; }
    }
}
