using DotnetBackendAnalyzers;
using Xunit;

namespace DotnetBackendAnalyzers.Tests;

public sealed class UseCaseServiceProviderInjectionAnalyzerTests
{
    [Fact]
    public async Task Reports_service_provider_injection_on_use_case()
    {
        var diagnostics = await AnalyzerTestHelper.GetDiagnosticsAsync(
            new UseCaseServiceProviderInjectionAnalyzer(),
            """
            using System;
            using System.Threading;
            using System.Threading.Tasks;

            public sealed class PlaceOrderUseCase
            {
                public PlaceOrderUseCase(IServiceProvider serviceProvider)
                {
                }

                public Task ExecuteAsync(CancellationToken cancellationToken) => Task.CompletedTask;
            }
            """);

        var diagnostic = Assert.Single(diagnostics);
        Assert.Equal("DBA1002", diagnostic.Id);
    }

    [Fact]
    public async Task Reports_service_provider_in_primary_constructor()
    {
        var diagnostics = await AnalyzerTestHelper.GetDiagnosticsAsync(
            new UseCaseServiceProviderInjectionAnalyzer(),
            """
            using System;

            public sealed class PlaceOrderHandler(IServiceProvider serviceProvider)
            {
            }
            """);

        var diagnostic = Assert.Single(diagnostics);
        Assert.Equal("DBA1002", diagnostic.Id);
    }

    [Fact]
    public async Task Reports_attribute_property_injection()
    {
        var diagnostics = await AnalyzerTestHelper.GetDiagnosticsAsync(
            new UseCaseServiceProviderInjectionAnalyzer(),
            """
            using System;

            public sealed class InjectAttribute : Attribute { }

            public sealed class PlaceOrderHandler
            {
                [Inject]
                public object Repository { get; set; } = new();
            }
            """);

        var diagnostic = Assert.Single(diagnostics);
        Assert.Equal("DBA1010", diagnostic.Id);
    }

    [Fact]
    public async Task Reports_handler_that_mixes_command_and_query_markers()
    {
        var diagnostics = await AnalyzerTestHelper.GetDiagnosticsAsync(
            new UseCaseServiceProviderInjectionAnalyzer(),
            """
            public interface ICommand<T> { }
            public interface IQuery<T> { }
            public sealed class CreateOrder : ICommand<string> { }
            public sealed class GetOrder : IQuery<string> { }

            public sealed class OrderHandler
            {
                public string Handle(CreateOrder command) => "";
                public string Handle(GetOrder query) => "";
            }
            """);

        var diagnostic = Assert.Single(diagnostics);
        Assert.Equal("DBA1011", diagnostic.Id);
    }

    [Fact]
    public async Task Reports_direct_repository_construction()
    {
        var diagnostics = await AnalyzerTestHelper.GetDiagnosticsAsync(
            new UseCaseServiceProviderInjectionAnalyzer(),
            """
            public sealed class SqlOrderRepository { }

            public sealed class PlaceOrderHandler
            {
                public object Handle() => new SqlOrderRepository();
            }
            """);

        var diagnostic = Assert.Single(diagnostics);
        Assert.Equal("DBA1012", diagnostic.Id);
    }

    [Fact]
    public async Task Allows_explicit_dependency_and_single_cqrs_role()
    {
        var diagnostics = await AnalyzerTestHelper.GetDiagnosticsAsync(
            new UseCaseServiceProviderInjectionAnalyzer(),
            """
            public interface ICommand<T> { }
            public interface IOrderRepository { }
            public sealed class CreateOrder : ICommand<string> { }

            public sealed class PlaceOrderHandler(IOrderRepository repository)
            {
                public string Handle(CreateOrder command) => "";
            }
            """);

        Assert.Empty(diagnostics);
    }

    [Fact]
    public async Task Does_not_treat_command_bus_as_command_marker()
    {
        var diagnostics = await AnalyzerTestHelper.GetDiagnosticsAsync(
            new UseCaseServiceProviderInjectionAnalyzer(),
            """
            public interface ICommandBus { }
            public interface IQueryBus { }

            public sealed class BusHandler
            {
                public void Handle(ICommandBus commandBus) { }
                public void Handle(IQueryBus queryBus) { }
            }
            """);

        Assert.Empty(diagnostics);
    }

    [Fact]
    public async Task Allows_canonical_use_case_interface_and_implementation()
    {
        var diagnostics = await AnalyzerTestHelper.GetDiagnosticsAsync(
            new UseCaseServiceProviderInjectionAnalyzer(),
            """
            using System.Threading;
            using System.Threading.Tasks;

            public sealed record PlaceOrderInput(string OrderId);
            public sealed record PlaceOrderOutput(string OrderId);

            public interface IPlaceOrderUseCase
            {
                Task<PlaceOrderOutput> ExecuteAsync(
                    PlaceOrderInput input,
                    CancellationToken cancellationToken);
            }

            public sealed class PlaceOrderUseCase : IPlaceOrderUseCase
            {
                public Task<PlaceOrderOutput> ExecuteAsync(
                    PlaceOrderInput input,
                    CancellationToken cancellationToken)
                    => Task.FromResult(new PlaceOrderOutput(input.OrderId));
            }
            """);

        Assert.Empty(diagnostics);
    }

    [Fact]
    public async Task Reports_optional_cancellation_token_on_use_case_contract()
    {
        var diagnostics = await AnalyzerTestHelper.GetDiagnosticsAsync(
            new UseCaseServiceProviderInjectionAnalyzer(),
            """
            using System.Threading;
            using System.Threading.Tasks;

            public interface IRefreshCacheUseCase
            {
                Task ExecuteAsync(CancellationToken cancellationToken = default);
            }
            """);

        var diagnostic = Assert.Single(diagnostics);
        Assert.Equal("DBA1015", diagnostic.Id);
    }

    [Fact]
    public async Task Reports_transport_command_as_use_case_input()
    {
        var diagnostics = await AnalyzerTestHelper.GetDiagnosticsAsync(
            new UseCaseServiceProviderInjectionAnalyzer(),
            """
            using System.Threading;
            using System.Threading.Tasks;

            public sealed record PlaceOrderCommand(string OrderId);

            public interface IPlaceOrderUseCase
            {
                Task ExecuteAsync(
                    PlaceOrderCommand command,
                    CancellationToken cancellationToken);
            }
            """);

        var diagnostic = Assert.Single(diagnostics);
        Assert.Equal("DBA1015", diagnostic.Id);
    }

    [Fact]
    public async Task Reports_http_result_as_use_case_output()
    {
        var diagnostics = await AnalyzerTestHelper.GetDiagnosticsAsync(
            new UseCaseServiceProviderInjectionAnalyzer(),
            """
            using System.Threading;
            using System.Threading.Tasks;

            public interface IActionResult { }

            public interface IPlaceOrderUseCase
            {
                Task<IActionResult> ExecuteAsync(CancellationToken cancellationToken);
            }
            """);

        var diagnostic = Assert.Single(diagnostics);
        Assert.Equal("DBA1015", diagnostic.Id);
    }

    [Fact]
    public async Task Reports_message_bus_and_other_use_case_dependencies()
    {
        var diagnostics = await AnalyzerTestHelper.GetDiagnosticsAsync(
            new UseCaseServiceProviderInjectionAnalyzer(),
            """
            using System.Threading;
            using System.Threading.Tasks;

            public interface IMessageBus { }
            public interface IReserveInventoryUseCase { }

            public sealed class PlaceOrderUseCase
            {
                public PlaceOrderUseCase(
                    IMessageBus bus,
                    IReserveInventoryUseCase reserveInventoryUseCase) { }

                public Task ExecuteAsync(CancellationToken cancellationToken)
                    => Task.CompletedTask;
            }
            """);

        Assert.Equal(2, diagnostics.Count(diagnostic => diagnostic.Id == "DBA1016"));
    }

    [Fact]
    public async Task Reports_use_case_that_also_exposes_handler_entry()
    {
        var diagnostics = await AnalyzerTestHelper.GetDiagnosticsAsync(
            new UseCaseServiceProviderInjectionAnalyzer(),
            """
            using System.Threading;
            using System.Threading.Tasks;

            public sealed class PlaceOrderUseCase
            {
                public Task ExecuteAsync(CancellationToken cancellationToken)
                    => Task.CompletedTask;

                public Task HandleAsync(CancellationToken cancellationToken)
                    => Task.CompletedTask;
            }
            """);

        var diagnostic = Assert.Single(diagnostics);
        Assert.Equal("DBA1015", diagnostic.Id);
    }

    [Fact]
    public async Task Allows_command_handler_that_adapts_to_one_use_case()
    {
        var diagnostics = await AnalyzerTestHelper.GetDiagnosticsAsync(
            new UseCaseServiceProviderInjectionAnalyzer(),
            """
            using System.Threading;
            using System.Threading.Tasks;

            public interface IPlaceOrderUseCase
            {
                Task ExecuteAsync(CancellationToken cancellationToken);
            }

            public sealed class PlaceOrderCommandHandler
            {
                public PlaceOrderCommandHandler(IPlaceOrderUseCase useCase) { }
            }
            """);

        Assert.Empty(diagnostics);
    }

    [Fact]
    public async Task Reports_command_handler_with_repository_dependency()
    {
        var diagnostics = await AnalyzerTestHelper.GetDiagnosticsAsync(
            new UseCaseServiceProviderInjectionAnalyzer(),
            """
            using System.Threading;
            using System.Threading.Tasks;

            public interface IPlaceOrderUseCase
            {
                Task ExecuteAsync(CancellationToken cancellationToken);
            }
            public interface IOrderRepository { }

            public sealed class PlaceOrderCommandHandler
            {
                public PlaceOrderCommandHandler(
                    IPlaceOrderUseCase useCase,
                    IOrderRepository repository) { }
            }
            """);

        var diagnostic = Assert.Single(diagnostics);
        Assert.Equal("DBA1017", diagnostic.Id);
    }
}
