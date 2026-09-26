using System.Runtime.CompilerServices;

namespace Procurement.Tests;

public sealed class ExternalIntegrationFactAttribute : FactAttribute
{
    public const string OptInVariable = "RUN_EXTERNAL_INTEGRATION_TESTS";
    public const string ConnectionVariable = "PROCUREMENT_TEST_POSTGRES_CONNECTION_STRING";

    public ExternalIntegrationFactAttribute([CallerFilePath] string sourceFilePath = "",
        [CallerLineNumber] int sourceLineNumber = 0) : base(sourceFilePath, sourceLineNumber)
    {
        if (!string.Equals(Environment.GetEnvironmentVariable(OptInVariable), "true", StringComparison.OrdinalIgnoreCase)
            || string.IsNullOrWhiteSpace(Environment.GetEnvironmentVariable(ConnectionVariable)))
            Skip = $"External PostgreSQL test. Set {OptInVariable}=true and {ConnectionVariable}.";
    }
}
