using System;
using System.Threading.Tasks;
using Microsoft.Extensions.DependencyInjection;
using NSubstitute;
using Xunit;

// TODO: Replace with Reqnroll bindings.
// [Binding]
namespace AiScrum.Tests.Steps;

public sealed class CreateTaskUseCaseSteps : IDisposable
{
    private readonly IServiceScope _scope;
    private readonly ScenarioState _state = new();

    public CreateTaskUseCaseSteps(TestHostFixture host)
    {
        // TODO: Wire TestHostFixture through Reqnroll DI container.
        _scope = host.Services.CreateScope();
    }

    public void Dispose() => _scope.Dispose();

    // [Given("a plan with a project exists")]
    public async Task GivenPlanWithProjectExists()
    {
        // TODO: Resolve use cases from DI when available.
        // var createPlan = _scope.ServiceProvider.GetRequiredService<ICreatePlanUseCase>();
        // var createProject = _scope.ServiceProvider.GetRequiredService<ICreateProjectUseCase>();

        _state.PlanId = Guid.NewGuid().ToString("N");
        _state.ProjectName = "Backend";
        _state.TaskName = "Implement API";

        await Task.CompletedTask;
    }

    // [Given("a plan id that does not exist")]
    public void GivenPlanIdDoesNotExist()
    {
        _state.PlanId = Guid.NewGuid().ToString("N");
        _state.ProjectName = "Backend";
        _state.TaskName = "Any Task";
    }

    // [Given("a plan exists without the project")]
    public void GivenPlanExistsWithoutProject()
    {
        _state.PlanId = Guid.NewGuid().ToString("N");
        _state.ProjectName = "Frontend";
        _state.TaskName = "Any Task";
    }

    // [When("I create a task")]
    // [When("I try to create a task")]
    public async Task WhenICreateATask()
    {
        // TODO: Resolve use case and execute.
        // var useCase = _scope.ServiceProvider.GetRequiredService<ICreateTaskUseCase>();
        // var input = new CreateTaskInput(_state.PlanId, _state.ProjectName, _state.TaskName);
        // _state.Output = await useCase.ExecuteAsync(input);

        await Task.CompletedTask;
    }

    // [Then("the task should be added to the project")]
    public void ThenTaskShouldBeAdded()
    {
        // TODO: Verify aggregate state via repository.
    }

    // [Then("a task created event should be published")]
    public void ThenTaskCreatedEventShouldBePublished()
    {
        // TODO: Use DomainEventCollector to assert event.
    }

    // [Then("the operation should fail with {string}")]
    public void ThenOperationShouldFailWith(string message)
    {
        // TODO: Assert output failure message.
        Assert.NotNull(message);
    }

    // [Then("the operation should be rejected with {string}")]
    public void ThenOperationShouldBeRejectedWith(string message)
    {
        Assert.NotNull(message);
    }

    // [Then("no events should be published")]
    public void ThenNoEventsShouldBePublished()
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
