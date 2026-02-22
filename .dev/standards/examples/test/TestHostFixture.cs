using System;
using System.Threading.Tasks;
using Microsoft.Extensions.DependencyInjection;
using Xunit;

namespace AiScrum.Tests.Infrastructure;

// Fixture-based test host (no base test classes).
public sealed class TestHostFixture : IAsyncLifetime
{
    public IServiceProvider Services { get; private set; } = default!;
    public string ActiveProfile { get; } = TestProfiles.Resolve();

    public Task InitializeAsync()
    {
        var services = new ServiceCollection();

        // Core infrastructure
        services.AddLogging();

        // TODO: Register ezDDD core services (DomainEventMapper, Contract, etc.)
        // TODO: Register Wolverine + EF Core based on profile
        if (ActiveProfile == TestProfiles.InMemory)
        {
            // TODO: Add in-memory repositories, message broker, and outbox store
            // services.AddInMemoryRepositories();
        }
        else if (ActiveProfile == TestProfiles.Outbox)
        {
            // TODO: Add PostgreSQL repositories and outbox pipeline
            // services.AddOutboxRepositories();
        }

        Services = services.BuildServiceProvider(validateScopes: true);
        return ClearStateAsync();
    }

    public Task DisposeAsync()
    {
        if (Services is IDisposable disposable)
        {
            disposable.Dispose();
        }

        return Task.CompletedTask;
    }

    public Task ClearStateAsync()
    {
        // TODO: Clear InMemory stores or reset Outbox tables.
        return Task.CompletedTask;
    }
}

public static class TestProfiles
{
    public const string InMemory = "Test.InMemory";
    public const string Outbox = "Test.Outbox";

    public static string Resolve()
    {
        var env = Environment.GetEnvironmentVariable("DOTNET_ENVIRONMENT");
        if (string.Equals(env, Outbox, StringComparison.OrdinalIgnoreCase))
        {
            return Outbox;
        }

        return InMemory;
    }
}
