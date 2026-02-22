using Example.Plans.Domain;
using Example.Plans.UseCases;
using Microsoft.Extensions.DependencyInjection;

namespace Example.Plans.Hosting;

public static class InMemoryRepositoryConfig
{
    public static IServiceCollection AddInMemoryRepositories(this IServiceCollection services)
    {
        // ezapp 2.x pattern (preferred):
        // TODO: replace with InMemory ORM + InMemory message db implementations.

        // Deprecated pattern (ezapp 1.x):
        // services.AddSingleton<IRepository<Plan, PlanId>, GenericInMemoryRepository>();

        // Placeholder repository registration.
        services.AddSingleton<IRepository<Plan, PlanId>, InMemoryPlanRepository>();
        return services;
    }
}

// TODO: Replace with actual in-memory repository implementation.
public sealed class InMemoryPlanRepository : IRepository<Plan, PlanId>
{
    private readonly Dictionary<string, Plan> _store = new();

    public Plan? FindById(PlanId id) => _store.TryGetValue(id.Value, out var plan) ? plan : null;

    public void Save(Plan aggregate) => _store[aggregate.Id.Value] = aggregate;
}
