using DotnetBackendValidation;
using Microsoft.EntityFrameworkCore;
using Xunit;

namespace DotnetBackendValidation.Tests;

public sealed class ProjectionModelRegistrationValidatorTests
{
    [Fact]
    public void Reports_marker_type_missing_from_ef_model()
    {
        using var context = new TestReadDbContext();

        var missing = ProjectionModelRegistrationValidator.FindUnregistered(
            new[]
            {
                typeof(RegisteredProjection),
                typeof(MissingProjection),
                typeof(DapperOnlyDto)
            },
            typeof(IProjectionReadModel),
            type => context.Model.FindEntityType(type) is not null);

        var projection = Assert.Single(missing);
        Assert.Equal(typeof(MissingProjection), projection);
    }

    [Fact]
    public void Ignores_abstract_and_non_marker_types()
    {
        var missing = ProjectionModelRegistrationValidator.FindUnregistered(
            new[]
            {
                typeof(AbstractProjection),
                typeof(DapperOnlyDto)
            },
            typeof(IProjectionReadModel),
            _ => false);

        Assert.Empty(missing);
    }

    private interface IProjectionReadModel;

    private sealed class RegisteredProjection : IProjectionReadModel
    {
        public int Id { get; set; }
    }

    private sealed class MissingProjection : IProjectionReadModel
    {
        public int Id { get; set; }
    }

    private abstract class AbstractProjection : IProjectionReadModel;

    private sealed class DapperOnlyDto;

    private sealed class TestReadDbContext : DbContext
    {
        protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
        {
            optionsBuilder.UseNpgsql("Host=localhost;Database=projection_validation");
        }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            modelBuilder.Entity<RegisteredProjection>().HasKey(projection => projection.Id);
        }
    }
}
