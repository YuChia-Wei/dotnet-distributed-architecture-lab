namespace SaleProducts.Applications.UseCases;

/// <summary>選擇並行 Consumer 範例使用的外部事件。</summary>
public enum ParallelWorkProbeMode
{
    /// <summary>單一處理器等待兩項並行作業。</summary>
    WhenAll,
    /// <summary>原始外部事件由兩個獨立處理器接收。</summary>
    IndependentHandlers,
}
