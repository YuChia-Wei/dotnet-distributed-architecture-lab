using Example.Plans.Outbox;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace Example.Plans.Hosting;

public static class OutboxRepositoryConfig
{
    public static IServiceCollection AddOutboxProfile(
        this IServiceCollection services,
        IConfiguration configuration)
    {
        services.AddPlanDataSource(configuration);
        services.AddOutboxRepositories(configuration);

        // TODO: configure Wolverine durable outbox + message broker
        return services;
    }
}
