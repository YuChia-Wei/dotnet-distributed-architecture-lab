namespace SaleOrders.Domains;

/// <summary>
/// 訂單狀態列舉
/// </summary>
public enum OrderStatus
{
    /// <summary>
    /// 已下單
    /// </summary>
    Placed,

    /// <summary>
    /// 已出貨
    /// </summary>
    Shipped,

    /// <summary>
    /// 已完成交付
    /// </summary>
    Delivered,

    /// <summary>
    /// 已取消
    /// </summary>
    Cancelled
}