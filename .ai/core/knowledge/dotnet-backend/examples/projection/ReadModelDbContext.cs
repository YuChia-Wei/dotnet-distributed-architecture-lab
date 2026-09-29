using Microsoft.EntityFrameworkCore;

namespace Example.Plans.ReadModel;

// TODO: Replace with real DbContext from the read-side project.
public sealed class ReadModelDbContext : DbContext
{
    public DbSet<PlanReadModel> Plans => Set<PlanReadModel>();
    public DbSet<TagReadModel> Tags => Set<TagReadModel>();
}
