using EfCoreWolverine.Host;
using JasperFx.CodeGeneration;
using JasperFx.CodeGeneration.Model;
using Microsoft.Extensions.DependencyInjection;
using Shouldly;
using Wolverine.Runtime.Handlers;

namespace EfCoreWolverine.Tests;

/// <summary>Verifies code generation and DI enrollment without substituting the production persistence pipeline.</summary>
public sealed class TransactionPipelineTests
{
    [Fact]
    public void Given_the_sample_host_when_the_handler_is_generated_then_one_EF_transaction_wraps_the_use_case()
    {
        using var host = SampleHost.BuildConsumer(new SampleSettings(
            "Host=localhost;Port=1;Database=unused;Username=unused;Timeout=1", "localhost:1",
            "unused.requests", "unused.events", "unused-group", "unused_messages"));
        var graph = host.Services.GetServices<ICodeFileCollection>().OfType<HandlerGraph>().Single();
        var chain = graph.ChainFor<DecreaseStockRequested>()!;
        ICodeFileCollection collection = graph;
        var assembly = collection.StartAssembly(collection.Rules);

        ((ICodeFile)chain).AssembleTypes(assembly);
        var source = assembly.GenerateCode(host.Services.GetRequiredService<IServiceVariableSource>());

        source.ShouldContain("EfCoreEnvelopeTransaction");
        source.ShouldContain("EnlistInOutboxAsync");
        source.ShouldContain("BeginTransactionAsync");
        source.ShouldContain("SaveChangesAsync");
        source.ShouldContain("CommitAsync");
        source.ShouldContain("RollbackAsync");
        source.IndexOf("BeginTransactionAsync", StringComparison.Ordinal)
            .ShouldBeLessThan(source.IndexOf("DecreaseStockHandler.Handle", StringComparison.Ordinal));
        source.IndexOf("DecreaseStockHandler.Handle", StringComparison.Ordinal)
            .ShouldBeLessThan(source.IndexOf("SaveChangesAsync", StringComparison.Ordinal));
        source.IndexOf("SaveChangesAsync", StringComparison.Ordinal)
            .ShouldBeLessThan(source.IndexOf("CommitAsync", StringComparison.Ordinal));
    }
}
