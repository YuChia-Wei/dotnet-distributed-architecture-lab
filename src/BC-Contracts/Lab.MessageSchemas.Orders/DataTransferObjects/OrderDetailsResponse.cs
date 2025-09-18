using System;
using System.Collections.Generic;

namespace Lab.MessageSchemas.Orders.DataTransferObjects;

/// <summary>
/// 訂單明細回應內容。
/// </summary>
public record OrderDetailsResponse
{
    /// <summary>
    /// 訂單識別碼。
    /// </summary>
    public Guid OrderId { get; init; }

    /// <summary>
    /// 訂單品項集合。
    /// </summary>
    public List<LineItemDto> LineItems { get; init; } = new();
}

/// <summary>
/// 訂單品項資訊。
/// </summary>
public record LineItemDto
{
    /// <summary>
    /// 商品識別碼。
    /// </summary>
    public Guid ProductId { get; init; }

    /// <summary>
    /// 品項數量。
    /// </summary>
    public int Quantity { get; init; }
}
