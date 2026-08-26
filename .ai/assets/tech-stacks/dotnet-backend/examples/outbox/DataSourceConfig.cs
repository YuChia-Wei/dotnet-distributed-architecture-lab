using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace Example.Plans.Outbox;

public static class DataSourceConfig
{
    public static IServiceCollection AddPlanDataSource(
        this IServiceCollection services,
        IConfiguration configuration)
    {
        var connectionString = configuration.GetConnectionString("PlanDb");
        // TODO: use Npgsql or SqlServer provider as needed.
        services.AddDbContext<PlanDbContext>(options =>
            options.UseNpgsql(connectionString));

        return services;
    }
}
