using DotnetBackendAnalyzers;
using Xunit;

namespace DotnetBackendAnalyzers.Tests;

public sealed class RepositoryQueryMethodAnalyzerTests
{
    [Fact]
    public async Task Allows_canonical_aggregate_repository_contract()
    {
        var diagnostics = await AnalyzeAsync(
            """
            using System.Threading.Tasks;

            public abstract class AggregateRoot<TId> { }
            public sealed class Order : AggregateRoot<string> { }

            public interface IAggregateRepository<TAggregate, TId>
                where TAggregate : AggregateRoot<TId>
            {
                Task<TAggregate?> FindByIdAsync(TId id);
                Task SaveAsync(TAggregate aggregate);
            }

            public interface IOrderRepository
                : IAggregateRepository<Order, string>
            {
            }
            """);

        Assert.Empty(diagnostics);
    }

    [Fact]
    public async Task Allows_compatibility_contract_that_inherits_canonical_contract()
    {
        var diagnostics = await AnalyzeAsync(
            """
            public abstract class AggregateRoot<TId> { }

            public interface IAggregateRepository<TAggregate, TId>
                where TAggregate : AggregateRoot<TId>
            {
            }

            public interface IDomainRepository<TAggregate, TId>
                : IAggregateRepository<TAggregate, TId>
                where TAggregate : AggregateRoot<TId>
            {
            }
            """);

        Assert.Empty(diagnostics);
    }

    [Fact]
    public async Task Reports_compatibility_contract_without_canonical_inheritance()
    {
        var diagnostics = await AnalyzeAsync(
            """
            public abstract class AggregateRoot<TId> { }

            public interface IDomainRepository<TAggregate, TId>
                where TAggregate : AggregateRoot<TId>
            {
            }
            """);

        Assert.Contains(diagnostics, diagnostic => diagnostic.Id == "DBA1001");
    }

    [Fact]
    public async Task Reports_query_or_batch_member_on_derived_aggregate_repository()
    {
        var diagnostics = await AnalyzeAsync(
            """
            using System.Collections.Generic;
            using System.Threading.Tasks;

            public abstract class AggregateRoot<TId> { }
            public sealed class Order : AggregateRoot<string> { }

            public interface IAggregateRepository<TAggregate, TId>
                where TAggregate : AggregateRoot<TId>
            {
            }

            public interface IOrderRepository : IAggregateRepository<Order, string>
            {
                Task<IReadOnlyList<Order>> FindByStatusAsync(string status);
                Task SaveAllAsync(IReadOnlyList<Order> orders);
            }
            """);

        Assert.Equal(2, diagnostics.Length);
        Assert.All(diagnostics, diagnostic => Assert.Equal("DBA1001", diagnostic.Id));
    }

    [Fact]
    public async Task Reports_approved_method_names_with_invalid_signatures()
    {
        var diagnostics = await AnalyzeAsync(
            """
            using System.Threading.Tasks;

            public abstract class AggregateRoot<TId> { }

            public interface IAggregateRepository<TAggregate, TId>
                where TAggregate : AggregateRoot<TId>
            {
                Task<object> FindByIdAsync(object id);
                void SaveAsync(object aggregate);
            }
            """);

        Assert.Equal(2, diagnostics.Length);
    }

    [Fact]
    public async Task Reports_child_entity_used_through_compatibility_contract()
    {
        var diagnostics = await AnalyzeAsync(
            """
            public abstract class AggregateRoot<TId> { }
            public sealed class OrderItem { }

            public interface IAggregateRepository<TAggregate, TId>
                where TAggregate : AggregateRoot<TId>
            {
            }

            public interface IDomainRepository<TAggregate, TId>
                : IAggregateRepository<TAggregate, TId>
                where TAggregate : AggregateRoot<TId>
            {
            }

            public interface IOrderItemRepository
                : IDomainRepository<OrderItem, string>
            {
            }
            """);

        var diagnostic = Assert.Single(diagnostics);
        Assert.Equal("DBA1001", diagnostic.Id);
        Assert.Equal(Microsoft.CodeAnalysis.DiagnosticSeverity.Error, diagnostic.Severity);
    }

    [Fact]
    public async Task Reports_query_repository_write_member()
    {
        var diagnostics = await AnalyzeAsync(
            """
            using System.Threading.Tasks;

            public interface IQueryRepository { }

            public interface IOrderQueryRepository : IQueryRepository
            {
                Task UpdateStatusAsync(string id);
            }
            """);

        var diagnostic = Assert.Single(diagnostics);
        Assert.Equal("DBA1001", diagnostic.Id);
    }

    [Fact]
    public async Task Reports_query_repository_returning_aggregate_or_entity()
    {
        var diagnostics = await AnalyzeAsync(
            """
            using System.Collections.Generic;
            using System.Threading.Tasks;

            public interface IQueryRepository { }
            public interface IAggregateRoot<TId> { }
            public interface IDomainEntity<TId> { }
            public sealed class Order : IAggregateRoot<string> { }
            public sealed class OrderItem : IDomainEntity<string> { }

            public interface IOrderQueryRepository : IQueryRepository
            {
                Task<Order?> FindOrderAsync(string id);
                Task<IReadOnlyList<OrderItem>> FindItemsAsync(string id);
            }
            """);

        Assert.Equal(2, diagnostics.Length);
    }

    [Fact]
    public async Task Allows_query_repository_returning_read_models_ids_and_scalars()
    {
        var diagnostics = await AnalyzeAsync(
            """
            using System.Collections.Generic;
            using System.Threading.Tasks;

            public interface IQueryRepository { }
            public sealed record OrderSummary(string Id);

            public interface IOrderQueryRepository : IQueryRepository
            {
                Task<OrderSummary?> FindSummaryAsync(string id);
                Task<IReadOnlyList<string>> FindIdsByStatusAsync(string status);
                Task<int> CountAsync();
            }
            """);

        Assert.Empty(diagnostics);
    }

    [Fact]
    public async Task Reports_public_generic_writable_crud_repository()
    {
        var diagnostics = await AnalyzeAsync(
            """
            public interface IRepository<TEntity, TId>
            {
                void Save(TEntity entity);
            }
            """);

        var diagnostic = Assert.Single(diagnostics);
        Assert.Equal("DBA1001", diagnostic.Id);
    }

    [Fact]
    public async Task Ignores_unrelated_repository_named_interfaces_and_capability_writers()
    {
        var diagnostics = await AnalyzeAsync(
            """
            public interface IRepositoryMetadata { }

            public interface IOutboxStore
            {
                void SaveMessage(object message);
            }

            public interface IProductAggregateBatchPort
            {
                void SaveAll(object products);
            }
            """);

        Assert.Empty(diagnostics);
    }

    private static Task<System.Collections.Immutable.ImmutableArray<Microsoft.CodeAnalysis.Diagnostic>>
        AnalyzeAsync(string source) =>
        AnalyzerTestHelper.GetDiagnosticsAsync(
            new RepositoryQueryMethodAnalyzer(),
            source);
}
