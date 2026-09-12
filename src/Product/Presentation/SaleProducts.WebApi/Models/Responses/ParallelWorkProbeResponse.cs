namespace SaleProducts.WebApi.Models.Responses;

/// <summary>回報已接受之外部事件診斷識別碼與目的地。</summary>
public sealed record ParallelWorkProbeResponse(Guid ProbeId, string Mode, string Topic, string Consumer);
