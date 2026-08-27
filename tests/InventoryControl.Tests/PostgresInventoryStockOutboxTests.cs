using Dapper;
using InventoryControl.Applications.Outbox;
using InventoryControl.Domains;
using InventoryControl.Infrastructure.Applications.Repositories;
using Lab.BoundedContextContracts.Inventory.IntegrationEvents;
using Lab.BuildingBlocks.Application;
using Lab.BuildingBlocks.Integrations;
using Npgsql;
using NSubstitute;
using Shouldly;

namespace InventoryControl.Tests;

public sealed class PostgresInventoryStockOutboxTests
{
    [ExternalIntegrationFact]
    public async Task given_a_stock_change_when_outbox_commit_succeeds_then_state_and_event_are_durable_together()
    {
        var connectionString = RequiredConnectionString();
        var item = new InventoryItem(Guid.CreateVersion7(), 5);
        var messageId = Guid.CreateVersion7();
        await using var connection = new NpgsqlConnection(connectionString);
        await connection.OpenAsync();
        await SeedAsync(connection, item);

        try
        {
            item.IncreaseStock(2);
            var adapter = new PostgresInventoryStockOutbox(
                connectionString,
                Substitute.For<IDomainEventDispatcher>());

            await adapter.SaveAndStageAsync(
                item,
                5,
                new InventoryOutboxMessage(
                    new ProductStockIncreasedIntegrationEvent(
                        item.Id,
                        item.ProductId,
                        2,
                        item.Stock),
                    new IntegrationMessageDelivery(messageId, item.ProductId.ToString("N"))),
                CancellationToken.None);

            var stock = await connection.QuerySingleAsync<int>(
                "SELECT Stock FROM InventoryItems WHERE Id = @Id",
                new { item.Id });
            var outboxCount = await connection.QuerySingleAsync<int>(
                "SELECT COUNT(*) FROM InventoryIntegrationOutbox WHERE Id = @MessageId",
                new { MessageId = messageId });
            stock.ShouldBe(7);
            outboxCount.ShouldBe(1);
        }
        finally
        {
            await CleanupAsync(connection, item.Id, messageId);
        }
    }

    [ExternalIntegrationFact]
    public async Task given_a_concurrent_stock_change_when_outbox_commit_runs_then_it_fails_without_an_event_row()
    {
        var connectionString = RequiredConnectionString();
        var item = new InventoryItem(Guid.CreateVersion7(), 5);
        var messageId = Guid.CreateVersion7();
        await using var connection = new NpgsqlConnection(connectionString);
        await connection.OpenAsync();
        await SeedAsync(connection, item);

        try
        {
            item.IncreaseStock(2);
            await connection.ExecuteAsync(
                "UPDATE InventoryItems SET Stock = 6 WHERE Id = @Id",
                new { item.Id });
            var adapter = new PostgresInventoryStockOutbox(
                connectionString,
                Substitute.For<IDomainEventDispatcher>());

            await Should.ThrowAsync<InventoryStockConcurrencyException>(() =>
                adapter.SaveAndStageAsync(
                    item,
                    5,
                    new InventoryOutboxMessage(
                        new ProductStockIncreasedIntegrationEvent(
                            item.Id,
                            item.ProductId,
                            2,
                            item.Stock),
                        new IntegrationMessageDelivery(messageId, item.ProductId.ToString("N"))),
                    CancellationToken.None));

            var stock = await connection.QuerySingleAsync<int>(
                "SELECT Stock FROM InventoryItems WHERE Id = @Id",
                new { item.Id });
            var outboxCount = await connection.QuerySingleAsync<int>(
                "SELECT COUNT(*) FROM InventoryIntegrationOutbox WHERE Id = @MessageId",
                new { MessageId = messageId });
            stock.ShouldBe(6);
            outboxCount.ShouldBe(0);
        }
        finally
        {
            await CleanupAsync(connection, item.Id, messageId);
        }
    }

    private static string RequiredConnectionString()
        => Environment.GetEnvironmentVariable(ExternalIntegrationFactAttribute.InventoryPostgresVariable)!;

    private static Task SeedAsync(NpgsqlConnection connection, InventoryItem item)
        => connection.ExecuteAsync(
            "INSERT INTO InventoryItems (Id, ProductId, Stock) VALUES (@Id, @ProductId, @Stock)",
            new { item.Id, item.ProductId, item.Stock });

    private static async Task CleanupAsync(NpgsqlConnection connection, Guid inventoryItemId, Guid messageId)
    {
        await connection.ExecuteAsync(
            "DELETE FROM InventoryIntegrationOutbox WHERE Id = @MessageId",
            new { MessageId = messageId });
        await connection.ExecuteAsync(
            "DELETE FROM InventoryItems WHERE Id = @InventoryItemId",
            new { InventoryItemId = inventoryItemId });
    }
}
