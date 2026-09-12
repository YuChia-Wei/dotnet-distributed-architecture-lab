namespace SaleProducts.Applications.UseCases;

/// <summary>請求一次實驗診斷；可提供識別碼以重播同一筆請求。</summary>
public sealed record TriggerParallelWorkProbeInput(ParallelWorkProbeMode Mode, Guid? ProbeId);
