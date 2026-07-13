using Example.Plans.Domain;
using Example.Plans.UseCases;
using Microsoft.Extensions.DependencyInjection;
using System.Threading;
using System.Threading.Tasks;

namespace Example.Plans.Hosting;

public static class InMemoryRepositoryConfig
{
    public static IServiceCollection AddInMemoryRepositories(this IServiceCollection services)
    {
        // ezapp 2.x pattern (preferred):
        // TODO: replace with InMemory ORM + InMemory message db implementations.

        // Placeholder repository registration.
        services.AddSingleton<IAggregateRepository<Plan, PlanId>, InMemoryPlanRepository>();
        return services;
    }
}

// TODO: Replace with actual in-memory repository implementation.
public sealed class InMemoryPlanRepository : IAggregateRepository<Plan, PlanId>
{
    private readonly Dictionary<string, Plan> _store = new();

    public Task<Plan?> FindByIdAsync(
        PlanId id,
        CancellationToken cancellationToken = default)
        => Task.FromResult(_store.TryGetValue(id.Value, out var plan) ? plan : null);

    public Task SaveAsync(
        Plan aggregate,
        CancellationToken cancellationToken = default)
    {
        _store[aggregate.Id.Value] = aggregate;
        return Task.CompletedTask;
    }
}
