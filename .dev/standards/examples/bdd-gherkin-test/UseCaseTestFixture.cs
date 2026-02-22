using System;
using Microsoft.Extensions.DependencyInjection;

namespace AiScrum.Tests.Infrastructure;

// Composition-based helper for use case tests (no inheritance).
public sealed class UseCaseTestFixture
{
    private readonly TestHostFixture _host;

    public UseCaseTestFixture(TestHostFixture host)
    {
        _host = host;
    }

    public IServiceScope CreateScope()
        => _host.Services.CreateScope();

    public string ActiveProfile => _host.ActiveProfile;

    public void ClearCapturedEvents()
    {
        // TODO: Clear DomainEventCollector state.
    }

    public DomainEventCollector GetEventCollector(IServiceProvider services)
        => services.GetRequiredService<DomainEventCollector>();
}

// Placeholder for the event collector until ezDDD .NET APIs are finalized.
public sealed class DomainEventCollector
{
    public void Clear() { }
    // TODO: Add collection APIs (Count, Last, OfType, etc.).
}
