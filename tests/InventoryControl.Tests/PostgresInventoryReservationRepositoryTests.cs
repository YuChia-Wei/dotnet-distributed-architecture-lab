using InventoryControl.Infrastructure.Applications.Repositories;
using Npgsql;
using Shouldly;

namespace InventoryControl.Tests;

public sealed class PostgresInventoryReservationRepositoryTests
{
    [ExternalIntegrationFact]
    [Trait("Category", "ExternalIntegration")]
    public async Task given_stock_for_only_one_request_when_two_reservations_run_concurrently_then_stock_and_outcomes_are_atomic()
    {
        // Given
        var connectionString = Environment.GetEnvironmentVariable(
            ExternalIntegrationFactAttribute.InventoryPostgresVariable)!;
        var inventoryItemId = Guid.CreateVersion7();
        var productId = Guid.CreateVersion7();
        var firstOperationId = Guid.CreateVersion7();
        var secondOperationId = Guid.CreateVersion7();
        await SeedAsync(connectionString, inventoryItemId, productId, 3);

        try
        {
            var repository = new PostgresInventoryReservationRepository(connectionString);

            // When
            var outcomes = await Task.WhenAll(
                repository.ReserveAsync(firstOperationId, productId, 2, CancellationToken.None),
                repository.ReserveAsync(secondOperationId, productId, 2, CancellationToken.None));

            // Then
            outcomes.Count(outcome => outcome.IsSuccess).ShouldBe(1);
            outcomes.Count(outcome => outcome.FailureReason == "InventoryIsNotEnough").ShouldBe(1);
            outcomes.ShouldAllBe(outcome => outcome.RemainingStock == 1);

            var durable = await ReadDurableStateAsync(connectionString, productId);
            durable.Stock.ShouldBe(1);
            durable.MinimumStock.ShouldBeGreaterThanOrEqualTo(0);
            durable.CompletedOperationCount.ShouldBe(2);
            durable.SuccessfulOperationCount.ShouldBe(1);
        }
        finally
        {
            await CleanupAsync(connectionString, inventoryItemId, firstOperationId, secondOperationId);
        }
    }

    private static async Task SeedAsync(string connectionString, Guid inventoryItemId, Guid productId, int stock)
    {
        await using var connection = new NpgsqlConnection(connectionString);
        await connection.OpenAsync();
        await using var command = connection.CreateCommand();
        command.CommandText = "INSERT INTO InventoryItems (Id, ProductId, Stock) VALUES (@id, @productId, @stock);";
        command.Parameters.AddWithValue("id", inventoryItemId);
        command.Parameters.AddWithValue("productId", productId);
        command.Parameters.AddWithValue("stock", stock);
        await command.ExecuteNonQueryAsync();
    }

    private static async Task<DurableState> ReadDurableStateAsync(string connectionString, Guid productId)
    {
        await using var connection = new NpgsqlConnection(connectionString);
        await connection.OpenAsync();
        await using var command = connection.CreateCommand();
        command.CommandText = """
            SELECT i.Stock,
                   LEAST(i.Stock, COALESCE(MIN(o.RemainingStock), i.Stock)) AS MinimumStock,
                   COUNT(o.OperationId) FILTER (WHERE o.CompletedAt IS NOT NULL) AS CompletedOperationCount,
                   COUNT(o.OperationId) FILTER (WHERE o.IsSuccess = TRUE) AS SuccessfulOperationCount
            FROM InventoryItems i
            LEFT JOIN InventoryReservationOperations o ON o.ProductId = i.ProductId
            WHERE i.ProductId = @productId
            GROUP BY i.Stock;
            """;
        command.Parameters.AddWithValue("productId", productId);
        await using var reader = await command.ExecuteReaderAsync();
        (await reader.ReadAsync()).ShouldBeTrue();
        return new DurableState(reader.GetInt32(0), reader.GetInt32(1), reader.GetInt64(2), reader.GetInt64(3));
    }

    private static async Task CleanupAsync(
        string connectionString,
        Guid inventoryItemId,
        Guid firstOperationId,
        Guid secondOperationId)
    {
        await using var connection = new NpgsqlConnection(connectionString);
        await connection.OpenAsync();
        await using var command = connection.CreateCommand();
        command.CommandText = """
            DELETE FROM InventoryReservationOperations WHERE OperationId IN (@firstOperationId, @secondOperationId);
            DELETE FROM InventoryItems WHERE Id = @inventoryItemId;
            """;
        command.Parameters.AddWithValue("firstOperationId", firstOperationId);
        command.Parameters.AddWithValue("secondOperationId", secondOperationId);
        command.Parameters.AddWithValue("inventoryItemId", inventoryItemId);
        await command.ExecuteNonQueryAsync();
    }

    private sealed record DurableState(
        int Stock,
        int MinimumStock,
        long CompletedOperationCount,
        long SuccessfulOperationCount);
}
