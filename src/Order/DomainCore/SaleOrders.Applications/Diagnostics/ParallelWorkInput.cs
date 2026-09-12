namespace SaleOrders.Applications.Diagnostics;

/// <summary>識別診斷作業請求的輸入，不依賴傳輸協定。</summary>
public sealed record ParallelWorkInput(Guid ProbeId);
