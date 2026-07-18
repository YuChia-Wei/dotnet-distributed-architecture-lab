using DotnetBackendAnalyzers;
using Xunit;

namespace DotnetBackendAnalyzers.Tests;

public sealed class EventSourcedAggregateMutationAnalyzerTests
{
    [Fact]
    public async Task Reports_direct_state_mutation_outside_when()
    {
        var diagnostics = await AnalyzerTestHelper.GetDiagnosticsAsync(
            new EventSourcedAggregateMutationAnalyzer(),
            """
            public abstract class EsAggregateRoot<TId> { }

            public sealed class Order : EsAggregateRoot<string>
            {
                public string State { get; private set; } = "New";

                public void Confirm()
                {
                    State = "Confirmed";
                }

                private void When(object @event)
                {
                    State = "Confirmed";
                }
            }
            """);

        var diagnostic = Assert.Single(diagnostics);
        Assert.Equal("DBA1009", diagnostic.Id);
    }

    [Fact]
    public async Task Allows_state_mutation_inside_when()
    {
        var diagnostics = await AnalyzerTestHelper.GetDiagnosticsAsync(
            new EventSourcedAggregateMutationAnalyzer(),
            """
            public abstract class EsAggregateRoot<TId> { }

            public sealed class Order : EsAggregateRoot<string>
            {
                public string State { get; private set; } = "New";

                private void When(object @event)
                {
                    State = "Confirmed";
                }
            }
            """);

        Assert.Empty(diagnostics);
    }

    [Fact]
    public async Task Does_not_apply_event_sourcing_rule_to_normal_aggregate()
    {
        var diagnostics = await AnalyzerTestHelper.GetDiagnosticsAsync(
            new EventSourcedAggregateMutationAnalyzer(),
            """
            public abstract class AggregateRoot<TId> { }

            public sealed class Order : AggregateRoot<string>
            {
                public string State { get; private set; } = "New";

                public void Confirm()
                {
                    State = "Confirmed";
                }
            }
            """);

        Assert.Empty(diagnostics);
    }

    [Fact]
    public async Task Reports_mutation_for_indirect_descendant_of_canonical_es_aggregate()
    {
        var diagnostics = await AnalyzerTestHelper.GetDiagnosticsAsync(
            new EventSourcedAggregateMutationAnalyzer(),
            """
            public abstract class EsAggregateRoot<TId> { }
            public abstract class ProductEsAggregate<TId> : EsAggregateRoot<TId> { }

            public sealed class Order : ProductEsAggregate<string>
            {
                public string State { get; private set; } = "New";

                public void Confirm()
                {
                    State = "Confirmed";
                }
            }
            """);

        var diagnostic = Assert.Single(diagnostics);
        Assert.Equal("DBA1009", diagnostic.Id);
    }

    [Fact]
    public async Task Does_not_apply_event_sourcing_rule_to_interface_first_normal_aggregate()
    {
        var diagnostics = await AnalyzerTestHelper.GetDiagnosticsAsync(
            new EventSourcedAggregateMutationAnalyzer(),
            """
            public interface IAggregateRoot<TId> { }

            public sealed class Order : IAggregateRoot<string>
            {
                public string State { get; private set; } = "New";

                public void Confirm()
                {
                    State = "Confirmed";
                }
            }
            """);

        Assert.Empty(diagnostics);
    }
}
