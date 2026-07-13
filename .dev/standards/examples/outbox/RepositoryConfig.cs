using Example.Plans.Domain;
using Example.Plans.UseCases;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.EntityFrameworkCore;
using System.Threading;
using System.Threading.Tasks;

namespace Example.Plans.Outbox;

public static class RepositoryConfig
{
    public static IServiceCollection AddOutboxRepositories(
        this IServiceCollection services,
        IConfiguration configuration)
    {
        // TODO: Configure Wolverine with PostgreSQL persistence + outbox.
        // Example (pseudo):
        // services.AddWolverine(opts =>
        // {
        //     opts.PersistMessagesWithPostgresql(configuration.GetConnectionString("MessageStore"));
        //     opts.UseDurableOutbox();
        // });

        services.AddScoped<IAggregateRepository<Plan, PlanId>, OutboxRepository>();
        return services;
    }
}

// TODO: Replace placeholder with ezDDD/Wolverine outbox repository integration.
public sealed class OutboxRepository : IAggregateRepository<Plan, PlanId>
{
    private readonly PlanDbContext _db;

    public OutboxRepository(PlanDbContext db)
    {
        _db = db;
    }

    public async Task<Plan?> FindByIdAsync(
        PlanId id,
        CancellationToken cancellationToken = default)
    {
        var data = await _db.Plans
            .AsNoTracking()
            .SingleOrDefaultAsync(x => x.PlanId == id.Value, cancellationToken);
        return data == null ? null : PlanOutboxMapper.ToDomain(data);
    }

    public async Task SaveAsync(
        Plan aggregate,
        CancellationToken cancellationToken = default)
    {
        var data = PlanOutboxMapper.ToData(aggregate);
        _db.Plans.Update(data);
        await _db.SaveChangesAsync(cancellationToken);
    }
}
