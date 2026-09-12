namespace SaleOrders.Consumer.Diagnostics;

/// <summary>提供分支的獨立服務範圍識別碼，供診斷記錄驗證。</summary>
public sealed class ParallelWorkScope
{
    /// <summary>目前服務範圍的識別碼。</summary>
    public Guid Id { get; } = Guid.NewGuid();
}
