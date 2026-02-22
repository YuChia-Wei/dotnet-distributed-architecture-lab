using Example.Plans.Domain;
using Example.Plans.UseCases;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

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

        services.AddScoped<IRepository<Plan, PlanId>, OutboxRepository>();
        return services;
    }
}

// TODO: Replace placeholder with ezDDD/Wolverine outbox repository integration.
public sealed class OutboxRepository : IRepository<Plan, PlanId>
{
    private readonly PlanDbContext _db;

    public OutboxRepository(PlanDbContext db)
    {
        _db = db;
    }

    public Plan? FindById(PlanId id)
    {
        var data = _db.Plans.Find(id.Value);
        return data == null ? null : PlanOutboxMapper.ToDomain(data);
    }

    public void Save(Plan aggregate)
    {
        var data = PlanOutboxMapper.ToData(aggregate);
        _db.Plans.Update(data);
        _db.SaveChanges();
    }
}
