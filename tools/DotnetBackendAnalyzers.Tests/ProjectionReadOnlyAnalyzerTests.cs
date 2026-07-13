using DotnetBackendAnalyzers;
using Xunit;

namespace DotnetBackendAnalyzers.Tests;

public sealed class ProjectionReadOnlyAnalyzerTests
{
    [Fact]
    public async Task Reports_db_context_save_changes_in_projection()
    {
        var diagnostics = await AnalyzerTestHelper.GetDiagnosticsAsync(
            new ProjectionReadOnlyAnalyzer(),
            """
            public interface IProjection { }
            public class DbContext
            {
                public void SaveChanges() { }
            }

            public sealed class OrderProjection : IProjection
            {
                private readonly DbContext dbContext = new();

                public void Execute()
                {
                    dbContext.SaveChanges();
                }
            }
            """);

        var diagnostic = Assert.Single(diagnostics);
        Assert.Equal("DBA1013", diagnostic.Id);
    }

    [Fact]
    public async Task Reports_db_set_update_in_projection()
    {
        var diagnostics = await AnalyzerTestHelper.GetDiagnosticsAsync(
            new ProjectionReadOnlyAnalyzer(),
            """
            public interface IProjection { }
            public class DbSet<T>
            {
                public void Update(T item) { }
            }

            public sealed class OrderProjection : IProjection
            {
                private readonly DbSet<object> orders = new();

                public void Execute(object order)
                {
                    orders.Update(order);
                }
            }
            """);

        var diagnostic = Assert.Single(diagnostics);
        Assert.Equal("DBA1013", diagnostic.Id);
    }

    [Fact]
    public async Task Allows_in_memory_collection_add_in_projection()
    {
        var diagnostics = await AnalyzerTestHelper.GetDiagnosticsAsync(
            new ProjectionReadOnlyAnalyzer(),
            """
            using System.Collections.Generic;

            public interface IProjection { }

            public sealed class OrderProjection : IProjection
            {
                public void Execute(List<object> results, object item)
                {
                    results.Add(item);
                }
            }
            """);

        Assert.Empty(diagnostics);
    }

    [Fact]
    public async Task Ignores_non_projection_service()
    {
        var diagnostics = await AnalyzerTestHelper.GetDiagnosticsAsync(
            new ProjectionReadOnlyAnalyzer(),
            """
            public class DbContext
            {
                public void SaveChanges() { }
            }

            public sealed class WriteRepository
            {
                public void Save(DbContext dbContext)
                {
                    dbContext.SaveChanges();
                }
            }
            """);

        Assert.Empty(diagnostics);
    }
}
