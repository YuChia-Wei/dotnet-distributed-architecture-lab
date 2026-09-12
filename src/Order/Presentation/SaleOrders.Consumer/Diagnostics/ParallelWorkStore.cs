using System.Collections.Concurrent;

namespace SaleOrders.Consumer.Diagnostics;

/// <summary>程序存活期間使用的範例儲存；重新啟動後資料與去重紀錄會消失。</summary>
/// <remarks>僅供有限期間的實驗使用，資料保留至程序結束。</remarks>
public sealed class ParallelWorkStore
{
    private readonly ConcurrentDictionary<Guid, byte> audit = new();
    private readonly ConcurrentDictionary<Guid, byte> statistics = new();

    /// <summary>冪等寫入一筆稽核紀錄，回傳是否新增。</summary>
    public bool WriteAudit(Guid probeId) => this.audit.TryAdd(probeId, 0);
    /// <summary>冪等記錄一筆統計，回傳是否新增。</summary>
    public bool RecordStatistics(Guid probeId) => this.statistics.TryAdd(probeId, 0);
    /// <summary>取得已寫入的稽核筆數。</summary>
    public int AuditCount => this.audit.Count;
    /// <summary>取得已記錄的統計筆數。</summary>
    public int StatisticsCount => this.statistics.Count;
}
