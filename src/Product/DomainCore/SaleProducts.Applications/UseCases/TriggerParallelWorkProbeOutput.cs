namespace SaleProducts.Applications.UseCases;

/// <summary>回報發佈已被接受，不代表 Consumer 作業已完成。</summary>
public sealed record TriggerParallelWorkProbeOutput(bool Accepted, Guid? ProbeId);
