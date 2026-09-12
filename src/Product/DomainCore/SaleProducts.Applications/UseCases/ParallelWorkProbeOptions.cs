namespace SaleProducts.Applications.UseCases;

/// <summary>明確啟用並行作業診斷事件的發佈功能。</summary>
public sealed record ParallelWorkProbeOptions(bool Enabled)
{
    /// <summary>控制診斷發佈功能的組態鍵。</summary>
    public const string EnabledConfigurationKey = "Diagnostics:ParallelWork:Enabled";
}
