using InventoryControl.Applications.Outbox;
using InventoryControl.Domains;
using InventoryControl.Infrastructure.Applications.Repositories;
using InventoryControl.Infrastructure.Persistence;
using Lab.BoundedContextContracts.Inventory.IntegrationEvents;
using Lab.BuildingBlocks.Application;
using Lab.BuildingBlocks.Integrations;
using Microsoft.EntityFrameworkCore;
using NSubstitute;
using Shouldly;

namespace InventoryControl.Tests;

/// <summary>AC3: stock and outgoing intent share one commit, including failure and stale-read paths.</summary>
public sealed class PostgresInventoryStockOutboxTests
{
    [ExternalIntegrationFact]
    public async Task given_a_stock_change_when_outbox_commit_succeeds_then_state_and_event_are_durable_together()
    {
        await using var database = await InventoryPostgresDatabase.CreateAsync();
        var item = await GivenStock(database, 5);
        var messageId = Guid.CreateVersion7();
        var error = await WhenIncreasingStock(database, item, 2, 5, messageId);
        error.ShouldBeNull();
        await ThenStockAndOutboxShouldBe(database, item.Id, messageId, 7, 1);
    }

    [ExternalIntegrationFact]
    public async Task given_a_concurrent_stock_change_when_outbox_commit_runs_then_it_fails_without_an_event_row()
    {
        await using var database = await InventoryPostgresDatabase.CreateAsync();
        var item = await GivenStock(database, 5);
        await GivenAnotherWriterChangedStock(database, item.Id, 6);
        var messageId = Guid.CreateVersion7();
        var error = await WhenIncreasingStock(database, item, 2, 5, messageId);
        error.ShouldBeOfType<InventoryStockConcurrencyException>();
        await ThenStockAndOutboxShouldBe(database, item.Id, messageId, 6, 0);
    }

    [ExternalIntegrationFact]
    public async Task given_invalid_outbox_metadata_when_staging_fails_then_stock_rolls_back_and_the_scope_can_reload()
    {
        await using var database = await InventoryPostgresDatabase.CreateAsync();
        var item = await GivenStock(database, 5);
        var messageId = Guid.CreateVersion7();
        await using var context = database.CreateContext();
        var repository = new InventoryItemDomainRepository(context, Substitute.For<IDomainEventDispatcher>());
        var tracked = (await repository.FindByIdAsync(item.Id))!;
        var error = await WhenIncreasingStock(context, tracked, 2, 5, messageId, new string('x', 65));
        ThenFailedScopeShouldBeClean(context, error);
        await ThenStockAndOutboxShouldBe(database, item.Id, messageId, 5, 0);
        var reloaded = await repository.FindByIdAsync(item.Id);
        reloaded!.Stock.ShouldBe(5);
        reloaded.ShouldNotBeSameAs(tracked);
    }

    [ExternalIntegrationFact]
    public async Task given_a_tracked_stock_item_when_a_set_based_commit_succeeds_then_later_reads_see_current_state()
    {
        await using var database = await InventoryPostgresDatabase.CreateAsync();
        var item = await GivenStock(database, 5);
        await using var context = database.CreateContext();
        var repository = new InventoryItemDomainRepository(context, Substitute.For<IDomainEventDispatcher>());
        var tracked = (await repository.FindByIdAsync(item.Id))!;
        var error = await WhenIncreasingStock(context, tracked, 2, 5, Guid.CreateVersion7(), item.ProductId.ToString("N"));
        error.ShouldBeNull();
        await GivenAnotherWriterChangedStock(database, item.Id, 8);
        await ThenReloadShouldReturnStock(repository, item.Id, 8);
    }

    private static async Task<InventoryItem> GivenStock(InventoryPostgresDatabase database, int stock)
    {
        var item = new InventoryItem(Guid.CreateVersion7(), stock);
        await using var context = database.CreateContext();
        context.InventoryItems.Add(item);
        await context.SaveChangesAsync();
        return item;
    }

    private static async Task GivenAnotherWriterChangedStock(InventoryPostgresDatabase database, Guid itemId, int stock)
    {
        await using var context = database.CreateContext();
        await context.InventoryItems.Where(item => item.Id == itemId).ExecuteUpdateAsync(setters => setters.SetProperty(item => item.Stock, stock));
    }

    private static async Task<Exception?> WhenIncreasingStock(InventoryPostgresDatabase database, InventoryItem item, int quantity, int expectedStock, Guid messageId)
    {
        await using var context = database.CreateContext();
        return await WhenIncreasingStock(context, item, quantity, expectedStock, messageId, item.ProductId.ToString("N"));
    }

    private static async Task<Exception?> WhenIncreasingStock(InventoryDbContext context, InventoryItem item, int quantity, int expectedStock, Guid messageId, string partitionKey)
    {
        item.IncreaseStock(quantity);
        var adapter = new PostgresInventoryStockOutbox(context, Substitute.For<IDomainEventDispatcher>());
        return await Record.ExceptionAsync(() => adapter.SaveAndStageAsync(item, expectedStock,
            new InventoryOutboxMessage(new ProductStockIncreasedIntegrationEvent(item.Id, item.ProductId, quantity, item.Stock),
                new IntegrationMessageDelivery(messageId, partitionKey)), CancellationToken.None));
    }

    private static async Task ThenStockAndOutboxShouldBe(InventoryPostgresDatabase database, Guid itemId, Guid messageId, int stock, int messageCount)
    {
        await using var context = database.CreateContext();
        (await context.InventoryItems.Where(item => item.Id == itemId).Select(item => item.Stock).SingleAsync()).ShouldBe(stock);
        (await context.OutboxMessages.CountAsync(message => message.Id == messageId)).ShouldBe(messageCount);
    }

    private static void ThenFailedScopeShouldBeClean(InventoryDbContext context, Exception? error)
    {
        error.ShouldBeOfType<InventoryOutboxTransientException>();
        context.ChangeTracker.Entries().ShouldBeEmpty();
    }

    private static async Task ThenReloadShouldReturnStock(InventoryItemDomainRepository repository, Guid itemId, int stock)
        => (await repository.FindByIdAsync(itemId))!.Stock.ShouldBe(stock);
}
