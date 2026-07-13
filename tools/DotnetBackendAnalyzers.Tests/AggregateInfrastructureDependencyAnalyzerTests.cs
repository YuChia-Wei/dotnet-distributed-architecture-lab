using DotnetBackendAnalyzers;
using Xunit;

namespace DotnetBackendAnalyzers.Tests;

public sealed class AggregateInfrastructureDependencyAnalyzerTests
{
    [Fact]
    public async Task Reports_db_context_reference_on_aggregate()
    {
        var diagnostics = await AnalyzerTestHelper.GetDiagnosticsAsync(
            new AggregateInfrastructureDependencyAnalyzer(),
            """
            namespace Microsoft.EntityFrameworkCore
            {
                public class DbContext { }
            }

            public sealed class OrderAggregate
            {
                private readonly Microsoft.EntityFrameworkCore.DbContext dbContext;

                public OrderAggregate(Microsoft.EntityFrameworkCore.DbContext dbContext)
                {
                    this.dbContext = dbContext;
                }
            }
            """);

        Assert.Contains(diagnostics, diagnostic => diagnostic.Id == "DBA1003");
    }
}
