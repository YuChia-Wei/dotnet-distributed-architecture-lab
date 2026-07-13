using DotnetBackendAnalyzers;
using Xunit;

namespace DotnetBackendAnalyzers.Tests;

public sealed class MapperComplianceAnalyzerTests
{
    [Fact]
    public async Task Reports_non_static_mapper()
    {
        var diagnostics = await AnalyzerTestHelper.GetDiagnosticsAsync(
            new MapperComplianceAnalyzer(),
            """
            public sealed class OrderMapper
            {
                public object ToDto(object source) => source;
            }
            """);

        var diagnostic = Assert.Single(diagnostics);
        Assert.Equal("DBA1007", diagnostic.Id);
    }

    [Fact]
    public async Task Allows_static_pure_mapper()
    {
        var diagnostics = await AnalyzerTestHelper.GetDiagnosticsAsync(
            new MapperComplianceAnalyzer(),
            """
            public sealed record OrderDto(string Id);
            public sealed record OrderData(string Id);

            public static class OrderMapper
            {
                public static OrderDto ToDto(OrderData source) => new(source.Id);
            }
            """);

        Assert.Empty(diagnostics);
    }

    [Fact]
    public async Task Reports_repository_dependency_on_mapper()
    {
        var diagnostics = await AnalyzerTestHelper.GetDiagnosticsAsync(
            new MapperComplianceAnalyzer(),
            """
            public interface IOrderRepository { }

            public static class OrderMapper
            {
                public static object ToDto(object source, IOrderRepository repository) => source;
            }
            """);

        var diagnostic = Assert.Single(diagnostics);
        Assert.Equal("DBA1008", diagnostic.Id);
    }

    [Fact]
    public async Task Ignores_non_mapper_types()
    {
        var diagnostics = await AnalyzerTestHelper.GetDiagnosticsAsync(
            new MapperComplianceAnalyzer(),
            """
            public interface IOrderRepository { }

            public sealed class OrderAssembler
            {
                private readonly IOrderRepository repository;

                public OrderAssembler(IOrderRepository repository)
                {
                    this.repository = repository;
                }
            }
            """);

        Assert.Empty(diagnostics);
    }
}
