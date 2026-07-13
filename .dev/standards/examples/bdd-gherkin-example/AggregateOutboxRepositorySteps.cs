using System;
using System.Threading.Tasks;
using Microsoft.Extensions.DependencyInjection;
using Xunit;

// TODO: Replace with Reqnroll bindings.
// [Binding]
namespace ExampleApp.Tests.Steps;

public sealed class AggregateOutboxRepositorySteps : IDisposable
{
    private readonly IServiceScope _scope;
    private readonly StepState _state = new();

    public AggregateOutboxRepositorySteps(TestHostFixture host)
    {
        // TODO: Wire TestHostFixture through Reqnroll DI container.
        _scope = host.Services.CreateScope();
    }

    public void Dispose() => _scope.Dispose();

    // [Given("a SampleAggregate aggregate with complete data")]
    public void GivenSampleAggregateWithCompleteData()
    {
        _state.AggregateId = $"test-aggregate-{DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()}";
        // TODO: Build a SampleAggregate with goal + definition-of-done.
    }

    // [Given("a aggregate exists in the database")]
    public async Task GivenSampleAggregateExistsInDatabase()
    {
        _state.AggregateId = $"test-aggregate-{DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()}";
        // TODO: Save aggregate via repository and flush.
        await Task.CompletedTask;
    }

    // [When("I save the aggregate using OutboxRepository")]
    public async Task WhenSaveSampleAggregate()
    {
        // TODO: repository.Save(aggregate)
        await Task.CompletedTask;
    }

    // [When("I load the aggregate from repository")]
    public async Task WhenLoadSampleAggregate()
    {
        // TODO: repository.FindById(...)
        await Task.CompletedTask;
    }

    // [When("I mark the aggregate as deleted and save")]
    public async Task WhenSoftDeleteSampleAggregate()
    {
        // TODO: aggregate.MarkAsDeleted(userId); repository.Save(aggregate)
        await Task.CompletedTask;
    }

    // [When("I update the aggregate and save")]
    public async Task WhenUpdateSampleAggregate()
    {
        // TODO: update entity + repository.Save(...)
        await Task.CompletedTask;
    }

    // [Then("the aggregate is persisted with all fields")]
    public void ThenSampleAggregatePersistedWithAllFields()
    {
        // TODO: Query database via EF Core to verify all fields.
        Assert.NotNull(_state.AggregateId);
    }

    // [Then("the aggregate data is fully rehydrated")]
    public void ThenSampleAggregateRehydrated()
    {
        // TODO: Assert fields on retrieved aggregate.
        Assert.NotNull(_state.AggregateId);
    }

    // [Then("the aggregate is marked as deleted in the database")]
    public void ThenSoftDeleted()
    {
        // TODO: Query is_deleted field.
        Assert.NotNull(_state.AggregateId);
    }

    // [Then("the version is incremented in storage")]
    public void ThenVersionIncremented()
    {
        // TODO: Assert optimistic version increment.
    }

    private sealed class StepState
    {
        public string? AggregateId { get; set; }
    }
}
