using System.Runtime.CompilerServices;

namespace SaleProducts.Tests;

/// <summary>Selects real Kafka tests only with explicit environment opt-in.</summary>
public sealed class KafkaParallelFactAttribute : FactAttribute
{
    public const string OptInVariable = "RUN_EXTERNAL_INTEGRATION_TESTS";
    public const string BootstrapVariable = "PARALLEL_TEST_KAFKA_BOOTSTRAP_SERVERS";

    public KafkaParallelFactAttribute([CallerFilePath] string? sourceFilePath = null,
        [CallerLineNumber] int sourceLineNumber = 0) : base(sourceFilePath, sourceLineNumber)
    {
        if (!Enabled) this.Skip = $"Real Kafka required: set {OptInVariable}=true and {BootstrapVariable}.";
    }

    public static bool Enabled => string.Equals(Environment.GetEnvironmentVariable(OptInVariable), "true",
        StringComparison.OrdinalIgnoreCase) && !string.IsNullOrWhiteSpace(Environment.GetEnvironmentVariable(BootstrapVariable));
}
