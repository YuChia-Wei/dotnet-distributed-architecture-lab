using EfCoreWolverine.Application;
using InventoryControl.Domains;
using InventoryControl.Domains.DomainEvents;
using Lab.BoundedContextContracts.Inventory.IntegrationEvents;
using Lab.BuildingBlocks.Application;
using NSubstitute;
using Shouldly;
using Xunit;

namespace EfCoreWolverine.Tests;

public sealed class DecreaseStockUseCaseTests : IDisposable
{
    private readonly IAggregateRepository<InventoryItem, Guid> _repository =
        Substitute.For<IAggregateRepository<InventoryItem, Guid>>();
    private readonly IStockEventPublisher _publisher = Substitute.For<IStockEventPublisher>();
    private readonly CancellationTokenSource _cancellation = new();
    private readonly List<string> _persistenceOrder = [];
    private InventoryItem? _inventoryItem;
    private DecreaseStockInput _input = new(Guid.NewGuid(), 1);
    private DecreaseStockOutput? _output;
    private ProductStockDecreasedIntegrationEvent? _publishedEvent;
    private Exception? _failure;

    [Fact]
    public async Task Given_available_stock_When_decreasing_stock_Then_save_precedes_publication()
    {
        Given_inventory_with_stock(10);
        Given_requested_quantity(3);
        Given_persistence_and_publication_are_observed();

        await When_the_use_case_executes();

        Then_the_operation_succeeds_with_stock(7);
        Then_the_repository_save_precedes_event_publication();
        Then_the_domain_event_is_preserved_and_mapped_to_the_integration_event();
        await Then_the_outbound_calls_receive_the_cancellation_token();
    }

    [Fact]
    public async Task Given_an_unknown_inventory_item_When_decreasing_stock_Then_return_not_found()
    {
        Given_an_unknown_inventory_item();

        await When_the_use_case_executes();

        Then_the_operation_fails_with("InventoryItemNotFound", null);
        await Then_no_save_or_publication_occurs();
    }

    [Fact]
    public async Task Given_insufficient_stock_When_decreasing_stock_Then_return_business_failure()
    {
        Given_inventory_with_stock(2);
        Given_requested_quantity(3);

        await When_the_use_case_executes();

        Then_the_operation_fails_with("InsufficientStock", 2);
        Then_the_aggregate_remains_unchanged_with_stock(2);
        await Then_no_save_or_publication_occurs();
    }

    [Theory]
    [InlineData(0)]
    [InlineData(-1)]
    public async Task Given_a_nonpositive_quantity_When_decreasing_stock_Then_reject_before_loading(int quantity)
    {
        Given_requested_quantity(quantity);

        await When_the_use_case_executes();

        Then_an_exception_of_type_is_raised<ArgumentOutOfRangeException>();
        await Then_no_repository_or_publisher_calls_occur();
    }

    [Fact]
    public async Task Given_an_empty_inventory_id_When_decreasing_stock_Then_reject_before_loading()
    {
        Given_an_empty_inventory_id();

        await When_the_use_case_executes();

        Then_an_exception_of_type_is_raised<ArgumentException>();
        await Then_no_repository_or_publisher_calls_occur();
    }

    [Fact]
    public async Task Given_a_persistence_failure_When_decreasing_stock_Then_propagate_without_publishing()
    {
        Given_inventory_with_stock(10);
        var expected = Given_persistence_fails();

        await When_the_use_case_executes();

        Then_the_original_exception_is_propagated(expected);
        Then_the_domain_event_remains_pending();
        await Then_no_publication_occurs();
    }

    [Fact]
    public async Task Given_a_publication_failure_When_decreasing_stock_Then_propagate_for_transaction_rollback()
    {
        Given_inventory_with_stock(10);
        var expected = Given_publication_fails();

        await When_the_use_case_executes();

        Then_the_original_exception_is_propagated(expected);
        Then_the_domain_event_remains_pending();
        await Then_the_save_was_requested();
    }

    private void Given_inventory_with_stock(int stock)
    {
        _inventoryItem = new InventoryItem(Guid.NewGuid(), stock);
        _input = new DecreaseStockInput(_inventoryItem.Id, 1);
        _repository.FindByIdAsync(_inventoryItem.Id, _cancellation.Token)
            .Returns(_inventoryItem);
    }

    private void Given_requested_quantity(int quantity) => _input = _input with { Quantity = quantity };

    private void Given_an_unknown_inventory_item()
    {
        _input = new DecreaseStockInput(Guid.NewGuid(), 1);
        _repository.FindByIdAsync(_input.InventoryItemId, _cancellation.Token)
            .Returns((InventoryItem?)null);
    }

    private void Given_an_empty_inventory_id() => _input = _input with { InventoryItemId = Guid.Empty };

    private void Given_persistence_and_publication_are_observed()
    {
        _repository.SaveAsync(Arg.Any<InventoryItem>(), Arg.Any<CancellationToken>())
            .Returns(_ =>
            {
                _persistenceOrder.Add("save");
                return Task.CompletedTask;
            });
        _publisher.PublishAsync(Arg.Any<ProductStockDecreasedIntegrationEvent>(), Arg.Any<CancellationToken>())
            .Returns(call =>
            {
                _persistenceOrder.Add("publish");
                _publishedEvent = call.Arg<ProductStockDecreasedIntegrationEvent>();
                return Task.CompletedTask;
            });
    }

    private Exception Given_persistence_fails()
    {
        var expected = new InvalidOperationException("Persistence failed.");
        _repository.SaveAsync(Arg.Any<InventoryItem>(), Arg.Any<CancellationToken>())
            .Returns(Task.FromException(expected));
        return expected;
    }

    private Exception Given_publication_fails()
    {
        var expected = new InvalidOperationException("Publication staging failed.");
        _publisher.PublishAsync(Arg.Any<ProductStockDecreasedIntegrationEvent>(), Arg.Any<CancellationToken>())
            .Returns(Task.FromException(expected));
        return expected;
    }

    private async Task When_the_use_case_executes()
    {
        var useCase = new DecreaseStockUseCase(_repository, _publisher);
        _failure = await Record.ExceptionAsync(async () =>
        {
            _output = await useCase.ExecuteAsync(_input, _cancellation.Token);
        });
    }

    private void Then_the_operation_succeeds_with_stock(int expectedStock)
    {
        _failure.ShouldBeNull();
        _output.ShouldBe(new DecreaseStockOutput(true, expectedStock, null));
        _inventoryItem.ShouldNotBeNull().Stock.ShouldBe(expectedStock);
    }

    private void Then_the_repository_save_precedes_event_publication() =>
        _persistenceOrder.ShouldBe(["save", "publish"]);

    private void Then_the_domain_event_is_preserved_and_mapped_to_the_integration_event()
    {
        var domainEvent = _inventoryItem.ShouldNotBeNull().DomainEvents.ShouldHaveSingleItem()
            .ShouldBeOfType<StockDecreased>();
        var integrationEvent = _publishedEvent.ShouldNotBeNull();
        integrationEvent.InventoryItemId.ShouldBe(domainEvent.InventoryItemId);
        integrationEvent.ProductId.ShouldBe(domainEvent.ProductId);
        integrationEvent.DecreasedQuantity.ShouldBe(_input.Quantity);
        integrationEvent.CurrentStock.ShouldBe(domainEvent.CurrentStock);
        integrationEvent.OccurredOn.ShouldBe(domainEvent.OccurredOn);
    }

    private async Task Then_the_outbound_calls_receive_the_cancellation_token()
    {
        await _repository.Received(1).FindByIdAsync(_input.InventoryItemId, _cancellation.Token);
        await _repository.Received(1).SaveAsync(_inventoryItem!, _cancellation.Token);
        await _publisher.Received(1).PublishAsync(_publishedEvent!, _cancellation.Token);
    }

    private void Then_the_operation_fails_with(string errorCode, int? expectedStock)
    {
        _failure.ShouldBeNull();
        _output.ShouldBe(new DecreaseStockOutput(false, expectedStock, errorCode));
    }

    private void Then_the_aggregate_remains_unchanged_with_stock(int expectedStock)
    {
        _inventoryItem.ShouldNotBeNull().Stock.ShouldBe(expectedStock);
        _inventoryItem.DomainEvents.ShouldBeEmpty();
    }

    private async Task Then_no_save_or_publication_occurs()
    {
        await _repository.DidNotReceive().SaveAsync(Arg.Any<InventoryItem>(), Arg.Any<CancellationToken>());
        await Then_no_publication_occurs();
    }

    private async Task Then_no_publication_occurs() =>
        await _publisher.DidNotReceive().PublishAsync(
            Arg.Any<ProductStockDecreasedIntegrationEvent>(), Arg.Any<CancellationToken>());

    private void Then_an_exception_of_type_is_raised<TException>() where TException : Exception
    {
        _failure.ShouldBeOfType<TException>();
        _output.ShouldBeNull();
    }

    private async Task Then_no_repository_or_publisher_calls_occur()
    {
        await _repository.DidNotReceive().FindByIdAsync(Arg.Any<Guid>(), Arg.Any<CancellationToken>());
        await Then_no_save_or_publication_occurs();
    }

    private void Then_the_original_exception_is_propagated(Exception expected)
    {
        _failure.ShouldBeSameAs(expected);
        _output.ShouldBeNull();
    }

    private void Then_the_domain_event_remains_pending() =>
        _inventoryItem.ShouldNotBeNull().DomainEvents.ShouldHaveSingleItem().ShouldBeOfType<StockDecreased>();

    private async Task Then_the_save_was_requested() =>
        await _repository.Received(1).SaveAsync(_inventoryItem!, _cancellation.Token);

    public void Dispose() => _cancellation.Dispose();
}
