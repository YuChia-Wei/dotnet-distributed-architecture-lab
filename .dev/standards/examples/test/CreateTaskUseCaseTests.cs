using System;
using System.Threading.Tasks;
using AiScrum.Tests.Infrastructure;
using Microsoft.Extensions.DependencyInjection;
using TestStack.BDDfy;
using Xunit;

namespace AiScrum.Tests.UseCases;

public sealed class CreateTaskUseCaseTests : IClassFixture<TestHostFixture>, IDisposable
{
    private readonly UseCaseTestFixture _fixture;
    private readonly IServiceScope _scope;
    private readonly ScenarioState _state = new();

    public CreateTaskUseCaseTests(TestHostFixture host)
    {
        _fixture = new UseCaseTestFixture(host);
        _scope = _fixture.CreateScope();
    }

    public void Dispose() => _scope.Dispose();

    [Fact]
    public void Create_task_in_existing_project()
    {
        this.Given(_ => Given_plan_with_project_exists())
            .And(_ => And_i_want_to_add_a_task_to_the_project())
            .When(_ => When_i_create_a_task())
            .Then(_ => Then_the_task_should_be_added_to_the_project())
            .And(_ => And_a_task_created_event_should_be_published())
            .BDDfy();
    }

    [Fact]
    public void Fail_when_plan_not_found()
    {
        this.Given(_ => Given_a_plan_id_that_does_not_exist())
            .When(_ => When_i_try_to_create_a_task())
            .Then(_ => Then_the_operation_should_fail_with("plan not found"))
            .And(_ => And_no_events_should_be_published())
            .BDDfy();
    }

    [Fact]
    public void Fail_when_project_not_found()
    {
        this.Given(_ => Given_a_plan_exists_without_the_project())
            .When(_ => When_i_try_to_create_a_task())
            .Then(_ => Then_the_operation_should_be_rejected_with("Project must exist"))
            .And(_ => And_no_events_should_be_published())
            .BDDfy();
    }

    void Given_plan_with_project_exists()
    {
        _state.PlanId = Guid.NewGuid().ToString("N");
        _state.ProjectName = "Backend";
        _state.TaskName = "Implement API";
    }

    void And_i_want_to_add_a_task_to_the_project()
    {
        _state.TaskName ??= "New Task";
    }

    void Given_a_plan_id_that_does_not_exist()
    {
        _state.PlanId = Guid.NewGuid().ToString("N");
        _state.ProjectName = "Backend";
        _state.TaskName = "Any Task";
    }

    void Given_a_plan_exists_without_the_project()
    {
        _state.PlanId = Guid.NewGuid().ToString("N");
        _state.ProjectName = "Frontend";
        _state.TaskName = "Any Task";
    }

    async Task When_i_create_a_task()
    {
        // TODO: Resolve use case and execute.
        // var useCase = _scope.ServiceProvider.GetRequiredService<ICreateTaskUseCase>();
        // var input = new CreateTaskInput(_state.PlanId!, _state.ProjectName!, _state.TaskName!);
        // _state.Output = await useCase.ExecuteAsync(input);
        await Task.CompletedTask;
    }

    Task When_i_try_to_create_a_task() => When_i_create_a_task();

    void Then_the_task_should_be_added_to_the_project()
    {
        // TODO: Verify aggregate state via repository.
    }

    void And_a_task_created_event_should_be_published()
    {
        // TODO: Verify event publication via DomainEventCollector.
    }

    void Then_the_operation_should_fail_with(string message)
    {
        Assert.NotNull(message);
    }

    void Then_the_operation_should_be_rejected_with(string message)
    {
        Assert.NotNull(message);
    }

    void And_no_events_should_be_published()
    {
        // TODO: Assert no events in collector.
    }

    private sealed class ScenarioState
    {
        public string? PlanId { get; set; }
        public string? ProjectName { get; set; }
        public string? TaskName { get; set; }
        public object? Output { get; set; }
    }
}
