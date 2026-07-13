using System.ComponentModel.DataAnnotations;

namespace SaleOrders.WebApi.Models.Requests;

/// <summary>Request body for an auditable order state transition.</summary>
public sealed record ChangeOrderStateRequest
{
    /// <summary>The business or operational reason for the transition.</summary>
    [Required(AllowEmptyStrings = false)]
    public required string Reason { get; init; }
}
