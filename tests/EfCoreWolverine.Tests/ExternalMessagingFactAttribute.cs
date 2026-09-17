using System.Runtime.CompilerServices;

namespace EfCoreWolverine.Tests;

public sealed class ExternalMessagingFactAttribute : FactAttribute
{
    public const string PostgresVariable = "EF_SAMPLE_POSTGRES";
    public const string KafkaVariable = "EF_SAMPLE_KAFKA";

    public static bool Enabled => Environment.GetEnvironmentVariable("RUN_EXTERNAL_INTEGRATION_TESTS") == "true"
        && !string.IsNullOrWhiteSpace(Environment.GetEnvironmentVariable(PostgresVariable))
        && !string.IsNullOrWhiteSpace(Environment.GetEnvironmentVariable(KafkaVariable));

    public ExternalMessagingFactAttribute([CallerFilePath] string? sourceFilePath = null,
        [CallerLineNumber] int sourceLineNumber = 0) : base(sourceFilePath, sourceLineNumber)
    {
        if (!Enabled) Skip = $"Set RUN_EXTERNAL_INTEGRATION_TESTS=true, {PostgresVariable}, and {KafkaVariable}.";
    }
}
