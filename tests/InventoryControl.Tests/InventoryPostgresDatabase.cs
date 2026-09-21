using InventoryControl.Infrastructure.Persistence;
using Microsoft.EntityFrameworkCore;
using Npgsql;

namespace InventoryControl.Tests;

/// <summary>Runs each integration scenario against the repository SQL schema without changing existing application rows.</summary>
internal sealed class InventoryPostgresDatabase(string adminConnectionString, string schemaName, string connectionString) : IAsyncDisposable
{
    public string ConnectionString { get; } = connectionString;

    public InventoryDbContext CreateContext()
        => new(new DbContextOptionsBuilder<InventoryDbContext>().UseNpgsql(this.ConnectionString).Options);

    public static async Task<InventoryPostgresDatabase> CreateAsync()
    {
        var adminConnectionString = Environment.GetEnvironmentVariable(ExternalIntegrationFactAttribute.InventoryPostgresVariable)
            ?? throw new InvalidOperationException("The opt-in PostgreSQL connection string is required.");
        var schemaName = "inventory_ef_tests_" + Guid.NewGuid().ToString("N");
        var builder = new NpgsqlConnectionStringBuilder(adminConnectionString) { SearchPath = schemaName, Pooling = false };
        var database = new InventoryPostgresDatabase(adminConnectionString, schemaName, builder.ConnectionString);
        await using var connection = new NpgsqlConnection(adminConnectionString);
        await connection.OpenAsync();
        await using var command = connection.CreateCommand();
        command.CommandText = $"CREATE SCHEMA \"{schemaName}\";";
        await command.ExecuteNonQueryAsync();
        try
        {
            await using var context = database.CreateContext();
            var schema = await File.ReadAllTextAsync(Path.Combine(AppContext.BaseDirectory, "Schema", "inventory.sql"));
            await context.Database.ExecuteSqlRawAsync(schema);
            return database;
        }
        catch
        {
            await database.DisposeAsync();
            throw;
        }
    }

    public async ValueTask DisposeAsync()
    {
        await using var connection = new NpgsqlConnection(adminConnectionString);
        await connection.OpenAsync();
        await using var command = connection.CreateCommand();
        command.CommandText = $"DROP SCHEMA IF EXISTS \"{schemaName}\" CASCADE;";
        await command.ExecuteNonQueryAsync();
    }
}
