using System;

namespace InventoryControl.WebApi.Models.Responses;

public record AvailableQuantityResponse
{
    /// <summary>
    /// 貨品識別碼。
    /// </summary>
    public Guid ProductId { get; init; }

    public int AvailableQuantity { get; init; }
}
