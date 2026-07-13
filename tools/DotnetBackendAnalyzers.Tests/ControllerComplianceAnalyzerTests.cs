using DotnetBackendAnalyzers;
using Xunit;

namespace DotnetBackendAnalyzers.Tests;

public sealed class ControllerComplianceAnalyzerTests
{
    [Fact]
    public async Task Reports_controller_without_api_controller_attribute()
    {
        var diagnostics = await AnalyzerTestHelper.GetDiagnosticsAsync(
            new ControllerComplianceAnalyzer(),
            """
            public sealed class ResourceController
            {
            }
            """);

        var diagnostic = Assert.Single(diagnostics);
        Assert.Equal("DBA1004", diagnostic.Id);
    }

    [Fact]
    public async Task Allows_abstract_controller_without_api_controller_attribute()
    {
        var diagnostics = await AnalyzerTestHelper.GetDiagnosticsAsync(
            new ControllerComplianceAnalyzer(),
            """
            public abstract class ResourceController
            {
            }
            """);

        Assert.Empty(diagnostics);
    }

    [Fact]
    public async Task Reports_db_context_dependency_in_controller()
    {
        var diagnostics = await AnalyzerTestHelper.GetDiagnosticsAsync(
            new ControllerComplianceAnalyzer(),
            """
            using System;

            public sealed class ApiControllerAttribute : Attribute { }
            public class DbContext { }
            public sealed class AppDbContext : DbContext { }

            [ApiController]
            public sealed class ResourceController
            {
                private readonly AppDbContext _dbContext;

                public ResourceController(AppDbContext dbContext)
                {
                    _dbContext = dbContext;
                }
            }
            """);

        Assert.Contains(diagnostics, diagnostic => diagnostic.Id == "DBA1005");
        Assert.DoesNotContain(diagnostics, diagnostic => diagnostic.Id == "DBA1004");
    }

    [Fact]
    public async Task Reports_save_changes_call_in_controller()
    {
        var diagnostics = await AnalyzerTestHelper.GetDiagnosticsAsync(
            new ControllerComplianceAnalyzer(),
            """
            using System;

            public sealed class ApiControllerAttribute : Attribute { }

            [ApiController]
            public sealed class ResourceController
            {
                public void Execute()
                {
                    SaveChanges();
                }

                private void SaveChanges() { }
            }
            """);

        var diagnostic = Assert.Single(diagnostics);
        Assert.Equal("DBA1005", diagnostic.Id);
    }

    [Fact]
    public async Task Reports_direct_handler_construction_in_controller()
    {
        var diagnostics = await AnalyzerTestHelper.GetDiagnosticsAsync(
            new ControllerComplianceAnalyzer(),
            """
            using System;

            public sealed class ApiControllerAttribute : Attribute { }
            public sealed class CreateResourceHandler { }

            [ApiController]
            public sealed class ResourceController
            {
                public object Execute() => new CreateResourceHandler();
            }
            """);

        var diagnostic = Assert.Single(diagnostics);
        Assert.Equal("DBA1006", diagnostic.Id);
    }

    [Fact]
    public async Task Reports_injected_handler_in_controller()
    {
        var diagnostics = await AnalyzerTestHelper.GetDiagnosticsAsync(
            new ControllerComplianceAnalyzer(),
            """
            using System;

            public sealed class ApiControllerAttribute : Attribute { }
            public sealed class CreateResourceHandler { }

            [ApiController]
            public sealed class ResourceController
            {
                private readonly CreateResourceHandler _handler;

                public ResourceController(CreateResourceHandler handler)
                {
                    _handler = handler;
                }
            }
            """);

        var diagnostic = Assert.Single(diagnostics);
        Assert.Equal("DBA1014", diagnostic.Id);
    }

    [Fact]
    public async Task Allows_injected_use_case_interface_in_controller()
    {
        var diagnostics = await AnalyzerTestHelper.GetDiagnosticsAsync(
            new ControllerComplianceAnalyzer(),
            """
            using System;

            public sealed class ApiControllerAttribute : Attribute { }
            public interface ICreateResourceUseCase { }

            [ApiController]
            public sealed class ResourceController
            {
                public ResourceController(ICreateResourceUseCase useCase) { }
            }
            """);

        Assert.Empty(diagnostics);
    }

    [Fact]
    public async Task Allows_query_repository_for_explicit_pure_query_profile()
    {
        var diagnostics = await AnalyzerTestHelper.GetDiagnosticsAsync(
            new ControllerComplianceAnalyzer(),
            """
            using System;

            public sealed class ApiControllerAttribute : Attribute { }
            public interface IQueryRepository { }
            public interface IProductQueryRepository : IQueryRepository { }

            [ApiController]
            public sealed class ProductQueryController
            {
                public ProductQueryController(IProductQueryRepository repository) { }
            }
            """);

        Assert.Empty(diagnostics);
    }

    [Fact]
    public async Task Reports_message_bus_injection_in_controller()
    {
        var diagnostics = await AnalyzerTestHelper.GetDiagnosticsAsync(
            new ControllerComplianceAnalyzer(),
            """
            using System;

            public sealed class ApiControllerAttribute : Attribute { }
            public interface IMessageBus { }

            [ApiController]
            public sealed class ResourceController
            {
                public ResourceController(IMessageBus bus) { }
            }
            """);

        var diagnostic = Assert.Single(diagnostics);
        Assert.Equal("DBA1014", diagnostic.Id);
    }
}
