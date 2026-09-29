using Microsoft.EntityFrameworkCore;

namespace Example.Plans.Outbox;

public sealed class PlanDbContext : DbContext
{
    public PlanDbContext(DbContextOptions<PlanDbContext> options) : base(options)
    {
    }

    public DbSet<PlanData> Plans => Set<PlanData>();
    public DbSet<ProjectData> Projects => Set<ProjectData>();
    public DbSet<TaskData> Tasks => Set<TaskData>();
    public DbSet<TaskTagData> TaskTags => Set<TaskTagData>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<ProjectData>()
            .HasMany(project => project.TaskDatas)
            .WithOne(task => task.ProjectData)
            .HasForeignKey(task => task.ProjectId);

        modelBuilder.Entity<PlanData>()
            .HasMany(plan => plan.ProjectDatas)
            .WithOne(project => project.PlanData)
            .HasForeignKey(project => project.PlanId);

        modelBuilder.Entity<TaskTagData>()
            .HasKey(tag => new { tag.TaskId, tag.TagId });

        modelBuilder.Entity<TaskData>()
            .HasMany(task => task.TagIds)
            .WithOne()
            .HasForeignKey(tag => tag.TaskId);
    }
}
