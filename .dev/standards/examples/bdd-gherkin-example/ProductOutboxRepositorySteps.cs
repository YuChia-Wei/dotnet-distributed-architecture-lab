using System;
using System.Threading.Tasks;
using Microsoft.Extensions.DependencyInjection;
using Xunit;

// TODO: Replace with Reqnroll bindings.
// [Binding]
namespace AiScrum.Tests.Steps;

public sealed class ProductOutboxRepositorySteps : IDisposable
{
    private readonly IServiceScope _scope;
    private readonly StepState _state = new();

    public ProductOutboxRepositorySteps(TestHostFixture host)
    {
        // TODO: Wire TestHostFixture through Reqnroll DI container.
        _scope = host.Services.CreateScope();
    }

    public void Dispose() => _scope.Dispose();

    // [Given("a Product aggregate with complete data")]
    public void GivenProductWithCompleteData()
    {
        _state.ProductId = $"test-product-{DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()}";
        // TODO: Build a Product with goal + definition-of-done.
    }

    // [Given("a product exists in the database")]
    public async Task GivenProductExistsInDatabase()
    {
        _state.ProductId = $"test-product-{DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()}";
        // TODO: Save product via repository and flush.
        await Task.CompletedTask;
    }

    // [When("I save the product using OutboxRepository")]
    public async Task WhenSaveProduct()
    {
        // TODO: repository.Save(product)
        await Task.CompletedTask;
    }

    // [When("I load the product from repository")]
    public async Task WhenLoadProduct()
    {
        // TODO: repository.FindById(...)
        await Task.CompletedTask;
    }

    // [When("I mark the product as deleted and save")]
    public async Task WhenSoftDeleteProduct()
    {
        // TODO: product.MarkAsDeleted(userId); repository.Save(product)
        await Task.CompletedTask;
    }

    // [When("I update the product and save")]
    public async Task WhenUpdateProduct()
    {
        // TODO: update entity + repository.Save(...)
        await Task.CompletedTask;
    }

    // [Then("the product is persisted with all fields")]
    public void ThenProductPersistedWithAllFields()
    {
        // TODO: Query database via EF Core to verify all fields.
        Assert.NotNull(_state.ProductId);
    }

    // [Then("the product data is fully rehydrated")]
    public void ThenProductRehydrated()
    {
        // TODO: Assert fields on retrieved aggregate.
        Assert.NotNull(_state.ProductId);
    }

    // [Then("the product is marked as deleted in the database")]
    public void ThenSoftDeleted()
    {
        // TODO: Query is_deleted field.
        Assert.NotNull(_state.ProductId);
    }

    // [Then("the version is incremented in storage")]
    public void ThenVersionIncremented()
    {
        // TODO: Assert optimistic version increment.
    }

    private sealed class StepState
    {
        public string? ProductId { get; set; }
    }
}
